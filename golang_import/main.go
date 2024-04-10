package main

import (
	"fmt"
	"log"
	"models"
	"net/http"
	"os"
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
	defer db.Close()

	fmt.Println("Successfully connect to database!")

	res, err := processCSVData(db, "output.xlsx", "PRODUCTS")
	if err != nil {
		fmt.Printf("Error while processing csv data: %s", err.Error())
		return
	}

	fmt.Println(res)
}

func processCSVData(db *gorm.DB, filePath string, uploadType string) ([]string, error) {
	db.AutoMigrate(
		&models.City{},
		&models.Characteristic{},
		&models.CharacteristicValue{},
		&models.Category{},
		&models.Price{},
		&models.Product{},
		&models.ProductImage{},
	)
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
	fmt.Printf("CSV data prodcessed in %.9fs.", time.Since(startTime).Seconds())
	return failedImages, nil
}

func productsProcess(db *gorm.DB, filePath string, ignoredColumns *Columns) error {

	xlFile, err := xlsx.OpenFile(fmt.Sprintf("../media/tmp/%s", filePath))
	if err != nil {
		log.Fatalf("Error opening XLSX file: %s\n", err)
		return err
	}
	ctNms := &Columns{
		cols: []string{},
	}

	var cities []models.City
	result := db.Find(&cities)
	if result.Error != nil {
		panic("failed to get cities: " + result.Error.Error())
	}

	// Iterate over each sheet in the XLSX file
	for _, sheet := range xlFile.Sheets {
		colNms := make(map[string]int, 0)
		chrCols := Columns{cols: []string{}}
		cityCols := make([]string, 0)
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
				panic("Не все обязательные поля найдены в документе")
			}
		}

		// Iterate over each row, start from second, in the sheet
		var colName string
		var tx *gorm.DB

		for _, row := range sheet.Rows[1:] {
			var idx int
			var prod models.Product
			var ctg models.Category
			var prntCtg models.Category

			tx = db.Begin()
			defer tx.Rollback() // Rollback transaction if commit is not called

			idx = colNms["CATEGORIES"]

			// Process categories
			processCategories(db, row.Cells[idx].String(), &ctg, &prntCtg)
			idx = colNms["TITLE"]

			processProduct(tx, row.Cells[idx].String(), &prod, &ctg)

			idx = colNms["PRIORITY"]
			processPriority(row.Cells[idx].String(), &prod)

			// idx = colNms["IMAGES"]
			// processImages(&prod, db, row.Cells[idx].String())

			// Process row's cells
			for idx, cell := range row.Cells {
				colName = sheet.Rows[0].Cells[idx].String()
				cellVal = cell.String()

				// Continue if cell is empty
				if cellVal == "" {
					fmt.Println("Empty cell, continue...")
					continue
				}
				fmt.Println(cellVal)

				if chrCols.Contains(colName) {
					processCharacteristics(ctg.ID, &prod, tx, cell, chrCols.cols)
				} else if ctNms.Contains(colName) {
					processPrices(&prod, tx, cellVal, colName, cities)
				} else {
					fmt.Printf("unexpected column name: %s Continue...\n", colName)
					continue
				}
			}
			fmt.Println()

			// Commit transaction if no errors occurred
			err = tx.Commit().Error
			if err != nil {
				fmt.Println(prod, prod.CategoryID, prod.Priority)
				log.Fatalf("error while commit transiction: %s; continue...", err)
				panic(err)
			}
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

func processProduct(tx *gorm.DB, cellVal string, prod *models.Product, ctg *models.Category) {
	if tx.Where(&models.Product{Title: cellVal}).First(&prod).RecordNotFound() {
		prod = &models.Product{Title: cellVal, Slug: slug.Make(cellVal), CategoryID: ctg.ID}
		tx.Create(&prod)
		fmt.Println("prod_id", prod.ID)
	} else {
		fmt.Printf("Product with title %s found\n", prod.Title)
	}
}

func processCategories(tx *gorm.DB, cellVal string, ctg, parentCategory *models.Category) {
	catNames := strings.Split(cellVal, " | ")
	var temp models.Category

	for _, catName := range catNames {

		temp = *ctg
		*ctg = *parentCategory
		*parentCategory = temp
		var category *models.Category
		// Check if the category already exists
		if tx.Where(&models.Category{Name: catName}).First(&category).RecordNotFound() {
			// If the category doesn't exist, create it
			category = &models.Category{Name: catName, Slug: slug.Make(catName), Parent: parentCategory}

			tx.Create(&category)

			// Set the parent category if provided
			if parentCategory != nil {
				category.ParentID = &parentCategory.ID
			}

			// Calculate left and right boundaries
			category.Left, category.Right = calculateBoundaries(tx, parentCategory)

			// Calculate the level of the category
			// category.Level = utils.CalculateLevel(category.Parent)

			// Set the tree ID (assuming it's always 1)
			category.TreeID = 1

			// Create the category
			fmt.Printf("Category %s created\n", catName)

			// Update ctg to the newly created category
			tx.Save(&category)
		} else {
			fmt.Printf("Category %s found, %s\n", catName, ctg.Name)
		}
		fmt.Println(category)
	}
	// Return the last processed category
}

func processPrices(prod *models.Product, tx *gorm.DB, cellVall string, colName string, cities []models.City) {
	var city models.City
	var price models.Price
	var err error

	idx := sort.Search(len(cities), func(i int) bool {
		return cities[i].Name >= colName
	})

	if !(idx < len(cities) && cities[idx].Name == colName) {
		fmt.Printf("city with name %s not found", colName)
		return
	}

	city = cities[idx]

	if tx.Where(&models.Price{CityID: city.ID, ProductID: prod.ID}).RecordNotFound() {
		price = models.Price{CityID: city.ID, ProductID: prod.ID}
		tx.Create(&price)
		fmt.Printf("Price for prod %d created\n", prod.ID)
	} else {
		// Price already exist
		// Set new price and old price
		price.OldPrice = &price.Price
		price.Price, err = strconv.ParseFloat(cellVall, 64)
		if err != nil {
			log.Fatalf("error while set new price: %s", err.Error())
			return
		}
		fmt.Printf("Price for prod %d updated\n", prod.ID)
	}
}

func processCharacteristics(ctgId uint, prod *models.Product, tx *gorm.DB, cell *xlsx.Cell, charsCols []string) {
	var char models.Characteristic
	var charVal models.CharacteristicValue
	for _, charCol := range charsCols {

		if tx.Where(&models.Characteristic{Name: charCol, CategoryID: ctgId}).RecordNotFound() {
			// If the record doesn't exist, create it
			char = models.Characteristic{Name: charCol, CategoryID: ctgId}
			tx.Create(&char)
			fmt.Printf("Char with name %s for prod %d created\n", char.Name, prod.ID)
		} else {
			fmt.Printf("Found char with name %s\n", char.Name)
		}

		if tx.Where(&models.CharacteristicValue{CharacteristicID: char.ID, ProductID: prod.ID}).RecordNotFound() {
			// If the record doesn't exist, create it
			charVal = models.CharacteristicValue{CharacteristicID: char.ID, ProductID: prod.ID}
			tx.Create(&charVal)
			fmt.Printf("Char val with value %s for prod %d created\n", charVal.Value, prod.ID)
		} else {
			// If the record exists, update it
			charVal.Value = cell.String()
			fmt.Printf("Char val with value %s for prod %d founded\n", charVal.Value, prod.ID)
		}
	}
}

func processImages(prod *models.Product, tx *gorm.DB, cell string) {
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
				utils.SaveImages(prod, tx, response, []string{"WATERMARK", "CATALOG", "SEARCH"})
			} else {
				utils.SaveImages(prod, tx, response, []string{"WATERMARK"})
			}
		}
	}
}

func (cols *Columns) Contains(v string) bool {
	idx := sort.Search(len(cols.cols), func(i int) bool {
		return cols.cols[i] >= v
	})

	return idx < len(cols.cols) && cols.cols[idx] == v
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
