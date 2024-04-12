package main

import (
	"fmt"
	"log"
	"models"
	"net/http"
	"os"
	"reflect"
	"sort"
	"strconv"
	"strings"
	"time"
	"utils"

	"github.com/gosimple/slug"
	"github.com/jinzhu/gorm"
	"github.com/joho/godotenv"
	_ "github.com/swaggo/http-swagger"
	"github.com/tealeg/xlsx"
)

type Columns struct {
	cols []string
}

func main() {
	err := godotenv.Load(".env")
	if err != nil {
		log.Fatal("Error loading .env file")
		return
	}

	dbHost := os.Getenv("POSTGRES_HOST")
	dbName := os.Getenv("POSTGRES_DB")
	dbUser := os.Getenv("POSTGRES_USER")
	dbPassword := os.Getenv("POSTGRES_PASSWORD")
	connStr := fmt.Sprintf("host=%s port=5432 user=%s dbname=%s password=%s sslmode=disable", dbHost, dbUser, dbName, dbPassword)

	db, err := gorm.Open("postgres", connStr)
	if err != nil {
		fmt.Println("Failed to connect to database!", err.Error())
		panic("Failed to connect to database")
	}

	tx := db.Begin()

	defer func() {
		if err := tx.Commit().Error; err != nil {
			fmt.Println(err)
			tx.Rollback()
		}
		if db.Error != nil {
			log.Fatalf(db.Error.Error())
			db.Rollback()
		}
		db.Close()
	}()

	fmt.Println("Successfully connect to database!")

	_, err = processCSVData(tx, "output.xlsx", "PRODUCTS")
	if err != nil {
		fmt.Printf("Error while processing csv data: %s", err.Error())
		return
	}
}

func processCSVData(db *gorm.DB, filePath string, uploadType string) ([]string, error) {
	for _, model := range []interface{}{
		&models.City{},
		&models.Characteristic{},
		&models.CharacteristicValue{},
		&models.Category{},
		&models.Price{},
		&models.Product{},
		&models.ProductImage{},
	} {
		if !db.HasTable(model) {
			panic(fmt.Sprintf("Table for model %s does not exist", reflect.TypeOf(model).Elem().Name()))
		}
	}

	// Parse CSV data and process accordingly based on uploadType
	var ignoredColumns = Columns{
		cols: []string{"TITLE", "IMAGES", "CATEGORIES", "SKU", "PRIORITY"},
	}
	var failedImages []string

	var startTime = time.Now()
	switch uploadType {
	case "PRODUCTS":
		err := productsProcess(db, filePath, &ignoredColumns)
		if err != nil {
			return nil, err
		}

	case "BRANDS":
		fmt.Println("BRAND data process")
		// Process brand data
		// Your logic for processing brands here
	default:
		return nil, fmt.Errorf("unknown upload type: %s, End time: %.9f", uploadType, time.Since(startTime).Seconds())
	}
	fmt.Printf("CSV data prodcessed in %.9fs.\n", time.Since(startTime).Seconds())
	return failedImages, nil
}

func productsProcess(db *gorm.DB, filePath string, ignoredColumns *Columns) error {

	colNms := make(map[string]int, 0)
	cityCols := make([]string, 0)
	chrCols := Columns{cols: []string{}}

	defer func() {
		fmt.Println(db.Error)
	}()

	xlFile, err := xlsx.OpenFile(fmt.Sprintf("../media/tmp/%s", filePath))
	if err != nil {
		log.Fatalf("Error opening XLSX file: %s\n", err)
		return err
	}
	ctNms := &Columns{
		cols: []string{},
	}

	// Select cities from db
	var cities []models.City
	result := db.Find(&cities)
	if result.Error != nil {
		return fmt.Errorf("failed to get cities: " + result.Error.Error())
	}

	// Insert city names into slice
	for _, c := range cities {
		ctNms.cols = append(ctNms.cols, c.Name)
	}

	// Iterate over each sheet in the XLSX file
	for _, sheet := range xlFile.Sheets {
		chrIdx := 0
		cityIdx := 0

		// Process column names
		var cellVal string
		for cIdx, cell := range sheet.Rows[0].Cells {
			cellVal = cell.String()
			colNms[cellVal] = cIdx

			if !ignoredColumns.Contains(cellVal) {

				// Select city and characteristic columns
				if ctNms.Contains(cellVal) {
					cityCols = append(cityCols, cellVal)
					cityIdx++
				} else {
					chrCols.cols = append(chrCols.cols, cellVal)
					chrIdx++
				}
			}
		}

		for _, el := range ignoredColumns.cols {
			if _, ok := colNms[el]; !ok {
				fmt.Println(el, ok)
				return fmt.Errorf("не все обязательные поля найдены в документе")
			}
		}

		// Iterate over each row, start from second, in the sheet
		var colName string

		for _, row := range sheet.Rows[1:] {
			idx := 0
			prod := models.Product{}
			ctg := models.Category{}
			prntCtg := models.Category{}

			idx = colNms["CATEGORIES"]

			// Initializer Transaction
			db.Transaction(func(tx *gorm.DB) error {

				var err error
				// Process categories
				if err = processCategories(db, row.Cells[idx].String(), &ctg, &prntCtg); err != nil {
					return nil
				}
				idx = colNms["TITLE"]

				processProduct(db, row.Cells[idx].String(), &prod, &ctg)

				idx = colNms["PRIORITY"]
				processPriority(row.Cells[idx].String(), &prod)

				idx = colNms["IMAGES"]
				processImages(&prod, db, row.Cells[idx].String())

				// Process row's cells
				for _, colName := range chrCols.cols {
					if err = processCharacteristics(ctg.ID, &prod, db, row.Cells[colNms[colName]], colName); err != nil {
						return err
					}
				}
				for _, colName = range cityCols {
					if err = processPrices(&prod, db, row.Cells[colNms[colName]].String(), colName, cities); err != nil {
						return err
					}
				}
				return nil
			})
			fmt.Printf("Product %s created\n", prod.Title)
		}
	}
	return nil
}

func processPriority(cellVal string, prod *models.Product) {
	if cellVal == "" {
		fmt.Println("Empty priority cell, continue...")
		return
	}

	priority, err := strconv.ParseFloat(cellVal, 32)
	if err != nil {
		log.Fatalf("error while parse priority: %s", err.Error())
		return
	}
	prod.Priority = int(priority)
}

func processProduct(tx *gorm.DB, cellVal string, prod *models.Product, ctg *models.Category) error {
	if tx.Where(&models.Product{Title: cellVal}).First(&prod).RecordNotFound() {
		newProd := models.Product{Title: cellVal, Slug: slug.Make(cellVal), CategoryID: ctg.ID, BrandID: nil}
		if err := tx.Create(&newProd).Error; err != nil {
			// Print error and return
			return err
		}
		*prod = newProd
	}
	return nil
}

func processCategories(tx *gorm.DB, cellVal string, ctg, parentCategory *models.Category) error {
	catNames := strings.Split(cellVal, " | ")

	var parentID *uint // Initialize parentID pointer
	for _, catName := range catNames {

		var category models.Category
		// Check if the category already exists
		if tx.Where(&models.Category{Name: catName}).First(&category).RecordNotFound() {
			// If the category doesn't exist, create it
			newCategory := models.Category{Name: catName, Slug: slug.Make(catName), ParentID: parentID}

			// Create the category
			if err := tx.Create(&newCategory).Error; err != nil {

				fmt.Println("Error creating category:", err)
				return err
			}

			// Calculate left and right boundaries
			newCategory.Left, newCategory.Right = calculateBoundaries(tx, parentCategory)

			// Calculate the level of the category and set treeID
			newCategory.Level = utils.CalculateLevel(newCategory.Parent)
			newCategory.TreeID = 1

			if err := tx.Save(&newCategory).Error; err != nil {
				fmt.Println(err)
				return err
			}

			// Update last checked category
			*ctg = newCategory

		} else {
			// Update last checked category
			*ctg = category
		}
		// Update parent category id
		parentID = &ctg.ID
		// if parentCategory != nil {
		// 	parentCategory.Children = append(parentCategory.Children, ctg)
		// 	ctg.Parent = parentCategory
		// 	if err := tx.Save(&ctg).Error; err != nil {
		// 		log.Fatal(err)
		// 		return err
		// 	}
		// }
	}
	return nil
}

func processPrices(prod *models.Product, tx *gorm.DB, cellVal string, colName string, cities []models.City) error {
	var city models.City
	var price models.Price
	var err error

	priceVal, err := strconv.ParseFloat(cellVal, 64)
	if err != nil {
		log.Fatalf("error while setting new price: %s", err.Error())
		return err
	}

	if find, err := findByField(cities, "Name", colName); err != nil {
		fmt.Println("City not found: ", colName)
		return err
	} else {
		city = find.(models.City)
	}

	if tx.Where(&models.Price{CityID: city.ID, ProductID: prod.ID}).First(&price).RecordNotFound() {
		newPrice := models.Price{CityID: city.ID, ProductID: prod.ID, Price: priceVal}
		if err := tx.Create(&newPrice).Error; err != nil {
			// Print error and return
			fmt.Println("Error creating price:", err)
			return err
		}

	} else {
		// Price already exist
		// Set new price and old price
		price.OldPrice = &price.Price
		price.Price = priceVal

		if err = tx.Save(&price).Error; err != nil {
			fmt.Println(err)
			return err
		}
	}
	return nil
}

func processCharacteristics(ctgId uint, prod *models.Product, tx *gorm.DB, cell *xlsx.Cell, charCol string) error {

	char := &models.Characteristic{}
	charVal := &models.CharacteristicValue{}
	val := cell.String()

	if tx.Where(&models.Characteristic{Name: charCol}).First(&char).RecordNotFound() {
		// If the record doesn't exist, create it
		newChar := models.Characteristic{Name: charCol, CategoryID: ctgId}
		if err := tx.Create(&newChar).Error; err != nil {
			// Print error and return
			fmt.Println("Error creating characteristic:", err, "\n", newChar, "\n", char, "\n", prod, "CATEGORY ID: -------  ", ctgId)
			return err
		}

		*char = newChar
	}

	if tx.Where(&models.CharacteristicValue{CharacteristicID: char.ID, ProductID: prod.ID}).First(&charVal).RecordNotFound() {
		// If the record doesn't exist, create it
		newCharVal := models.CharacteristicValue{CharacteristicID: char.ID, ProductID: prod.ID, Value: val}
		if err := tx.Create(&newCharVal).Error; err != nil {
			// Print error and return
			fmt.Println("Error creating characteristic value:", err)
			return err
		}

		*charVal = newCharVal
	} else {
		// If the record exists, update it
		charVal.Value = cell.String()
		if err := tx.Save(charVal).Error; err != nil {
			fmt.Println(err)
			return err
		}
	}
	return nil
}

func processImages(prod *models.Product, tx *gorm.DB, cell string) error {
	imgs := strings.Split(cell, ",")

	if len(imgs) > 0 {
		for idx, imgUrl := range imgs {
			response, err := http.Get(imgUrl)
			if err != nil {
				log.Fatalf("error while get image by url %s", imgUrl)
				fmt.Println(err.Error())
				continue
			}
			defer response.Body.Close()

			if idx == 0 {
				if err := utils.SaveImages(prod, tx, response, []string{"WATERMARK", "CATALOG", "SEARCH"}); err != nil {
					return err
				}
			} else {
				if err := utils.SaveImages(prod, tx, response, []string{"WATERMARK"}); err != nil {
					return err
				}
			}
		}
	}
	return nil
}

func (cols *Columns) Contains(el string) bool {
	sort.Strings(cols.cols)

	low := 0
	slice := cols.cols
	high := len(slice) - 1

	for low <= high {
		mid := (low + high) / 2
		if slice[mid] == el {
			return true
		} else if slice[mid] < el {
			low = mid + 1
		} else {
			high = mid - 1
		}
	}

	return false
}

// findByField finds an element in the slice of any structs by the provided field value.
func findByField(slice interface{}, field string, value interface{}) (interface{}, error) {
	sliceValue := reflect.ValueOf(slice)
	if sliceValue.Kind() != reflect.Slice {
		return nil, fmt.Errorf("findByField: kind %s not a slice", sliceValue.Kind())
	}

	for i := 0; i < sliceValue.Len(); i++ {
		item := sliceValue.Index(i)
		if item.Kind() != reflect.Struct {
			return nil, fmt.Errorf("findByField: not a slice of structs")
		}

		fieldValue := item.FieldByName(field)
		if !fieldValue.IsValid() {
			continue
		}

		if reflect.DeepEqual(fieldValue.Interface(), value) {
			return item.Interface(), nil
		}
	}

	return nil, fmt.Errorf("value %s not found in provided slice", value)
}

// Calculate left and right boundaries for the new node
func calculateBoundaries(db *gorm.DB, parent *models.Category) (int, int) {
	if parent == nil {
		// If the node has no parent, set lft to 1 and rght to 2
		return 1, 2
	}

	// Find the maximum right boundary of the parent's children
	maxRght := db.Model(&models.Category{}).
		Where("parent_id = ?", parent.ID).
		Select("MAX(rght)").
		Row()

	var maxRghtValue int
	if err := maxRght.Scan(&maxRghtValue); err != nil {
		// Handle error
		return 0, 0
	}

	// Set lft to the maximum right boundary of the parent's children
	lft := maxRghtValue + 1
	// Set rght to lft + 1
	rght := lft + 1
	return lft, rght
}
