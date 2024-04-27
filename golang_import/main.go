package main

import (
	"auth"
	"fmt"
	"log"
	"models"
	"net/http"
	"os"
	"path/filepath"
	"reflect"
	"sort"
	"strconv"
	"strings"
	"time"
	"utils"

	"github.com/gin-gonic/gin"

	"github.com/gosimple/slug"
	"github.com/jinzhu/gorm"
)

var db *gorm.DB

func init() {
	var err error
	var (
		dbHost     = os.Getenv("POSTGRES_HOST")
		dbName     = os.Getenv("POSTGRES_DB")
		dbUser     = os.Getenv("POSTGRES_USER")
		dbPassword = os.Getenv("POSTGRES_PASSWORD")
	)
	connStr := fmt.Sprintf("host=%s port=5432 user=%s dbname=test_%s password=%s sslmode=disable", dbHost, dbUser, dbName, dbPassword)

	db, err = gorm.Open("postgres", connStr)
	if err != nil {
		msg := "Failed to connect to database!"
		fmt.Println(msg, err.Error())
		log.Fatal(err.Error())
		return
	}

	fmt.Println("Successfully connect to database!")

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
			msg := fmt.Sprintf("Table for model %s does not exist", reflect.TypeOf(model).Elem().Name())
			log.Fatal(msg)
			return
		}
	}
}

func main() {
	fmt.Println("Initializing golang server...")
	router := gin.Default()

	authGroup := router.Group("/api/upload")

	authGroup.Use(auth.AuthMiddleware())

	authGroup.PUT("/:filename", processXLSXData)

	router.Run(":8080")
	fmt.Println("Golang server started")
}

func processXLSXData(c *gin.Context) {

	filename := c.Param("filename")

	// Retrieve upload type from query parameters
	uploadType := c.Query("type")

	tmpDir := "../media/tmp"
	if err := os.MkdirAll(tmpDir, os.ModePerm); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error. Unable to create directory: " + err.Error()})
		return
	}
	flPth := filepath.Join(tmpDir, filename)

	// Try to get file from request
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Save the file to disk
	err = c.SaveUploadedFile(file, flPth)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	// Parse CSV data and process accordingly based on uploadType
	var ignoredColumns = []string{"TITLE", "IMAGES", "CATEGORIES", "SKU", "PRIORITY"}
	var startTime = time.Now()

	switch uploadType {
	case "PRODUCTS":
		c.JSON(http.StatusOK, gin.H{"message": "Success authorized, products process started..."})
		go func() {
			err := productsProcess(db, flPth, ignoredColumns)
			if err != nil {
				fmt.Println(err.Error())
				return
			}
			fmt.Printf("Products data processed in %.9fs.\n", time.Since(startTime).Seconds())
		}()

	case "BRANDS":
		go func() {
			fmt.Println("BRAND data process")
			c.JSON(http.StatusOK, gin.H{"message": "Success authorized, brands process started..."})

			// Process brand data
			// Your logic for processing brands here
			fmt.Printf("BRAND data prodcessed in %.9fs.\n", time.Since(startTime).Seconds())
		}()
	default:
		c.JSON(http.StatusInternalServerError, gin.H{"error": "unknown upload type: " + uploadType})
	}
}

func productsProcess(db *gorm.DB, filePath string, ignoredColumns []string) error {
	colNms := make(map[string]int, 0)

	r, err := utils.NewReader(filePath, ignoredColumns)
	if err != nil {
		log.Fatalf("error while create new reader: %s", err.Error())
		return err
	}

	defer func() {
		fmt.Println("Products processed, remove tmp file")
		if err := os.Remove(filePath); err == nil {
			fmt.Println("tmp file successfully deleted")
		} else {
			fmt.Println("tmp file not found, exit.")
		}
		r.Close()
	}()

	// Select cities from db
	var cities []models.CityGroup
	result := db.Find(&cities)
	if result.Error != nil {
		return fmt.Errorf("failed to get cities: " + result.Error.Error())
	}

	// Сортируем массив по полю Name
	sort.Slice(cities, func(i, j int) bool {
		return cities[i].Name < cities[j].Name
	})

	// Insert city names into slice
	for _, c := range cities {
		r.GetFileReader().CtNms.Cols = append(r.GetFileReader().CtNms.Cols, c.Name)
	}

	// Iterate over each row, start from second, in the sheet

	rows, err := r.Read()
	if err != nil {
		return err
	}

	for i, col := range r.GetFileReader().Columns {
		colNms[col] = i
	}

	for idx, row := range rows[1:] {

		prod := models.Product{}
		ctg := models.Category{}

		idx = colNms["CATEGORIES"]

		// Initializer Transaction
		db.Transaction(func(tx *gorm.DB) error {

			var err error
			var prntID *uint
			var chrCol string
			var ctCol string
			// Process categories
			if err = processCategories(db, row[idx], &ctg, prntID); err != nil {
				return err
			}

			if err = processProduct(db, row, &prod, &ctg, colNms); err != nil {
				fmt.Println("Error while process product: ", err.Error())
				return err
			}

			// Process row's cells
			for _, chrCol = range r.GetFileReader().ChrCols.Cols {
				idx, ok := colNms[chrCol]
				if !ok {
					continue
				}

				chrVal, err := utils.GetFromSlice(row, idx)
				if err != nil {
					continue
				}

				if err = processCharacteristics(ctg.ID, &prod, db, chrVal, chrCol); err != nil {
					return err
				}
			}
			// fmt.Println(colNms, r.GetFileReader().CtNms.Cols)

			for _, ctCol = range r.GetFileReader().CtNms.Cols {
				idx, ok := colNms[ctCol]
				if !ok {
					continue
				}

				ctVal, err := utils.GetFromSlice(row, idx)
				if err != nil {
					fmt.Println(err.Error())
					continue
				}
				fmt.Println(ctVal)

				if err = processPrices(&prod, db, ctVal, ctCol, cities); err != nil {
					fmt.Println(err.Error())
				}
			}
			fmt.Printf("Product %s processed\n", prod.Title)
			return nil
		})
	}
	return nil
}

func processProduct(tx *gorm.DB, row []string, prod *models.Product, ctg *models.Category, colNms map[string]int) error {
	var title string
	var dsc string

	idx, ok := colNms["SKU"]
	if !ok {
		return fmt.Errorf("SKU column is required")
	}
	cellVal, err := utils.GetFromSlice(row, idx)
	if err != nil {
		return err
	}

	idx, ok = colNms["TITLE"]
	if !ok {
		title = "TITLE"
	} else {
		title, err = utils.GetFromSlice(row, idx)
		if err != nil {
			return err
		}
	}

	if idx, ok := colNms["DESCRIPTION"]; ok {
		dsc, err = utils.GetFromSlice(row, idx)
		if err != nil {
			return err
		}
	} else {
		dsc = "Нет описания"
	}

	slg := slug.Make(title)
	if tx.Where(&models.Product{Article: cellVal, Slug: slg}).First(&prod).RecordNotFound() {
		newProd := models.Product{Article: cellVal, Title: title, Slug: slg, CategoryID: ctg.ID, BrandID: nil}
		if err := tx.Create(&newProd).Error; err != nil {
			return err
		}
		*prod = newProd
	}

	// Set Priority
	idx, ok = colNms["PRIORITY"]
	if ok {
		cellVal, err = utils.GetFromSlice(row, idx)
		if err == nil {
			if cellVal != "" {
				priority, err := strconv.ParseFloat(cellVal, 32)
				if err == nil {
					prod.Priority = int(priority)
				}
			}
		}
	}
	if !ok || err != nil {
		prod.Priority = 500
	}

	prod.Description = dsc
	prod.Title = title

	if err = tx.Save(&prod).Error; err != nil {
		return err
	}

	// Set Images
	if idx, ok := colNms["IMAGES"]; ok {
		cellVal, err = utils.GetFromSlice(row, idx)
		if err != nil {
			return err
		}
		if err = processImages(cellVal, prod, tx); err != nil {
			return err
		}
	}
	return nil
}

func processImages(cellVal string, prod *models.Product, tx *gorm.DB) error {
	imgs := strings.Split(cellVal, ",")

	if len(imgs) > 0 {
		var bsName string
		for idx, imgUrl := range imgs {
			bsName = strings.Split(filepath.Base(imgUrl), ".")[0]

			response, err := http.Get(imgUrl)
			if err != nil {
				log.Fatalf("error while get image by url %s", imgUrl)
				fmt.Println(err.Error())
				continue
			}
			defer response.Body.Close()

			if idx == 0 {
				if err := utils.SaveImages(bsName, prod, tx, response, []string{"WATERMARK", "CATALOG", "SEARCH"}); err != nil {
					return err
				}
			} else {
				if err := utils.SaveImages(bsName, prod, tx, response, []string{"WATERMARK"}); err != nil {
					return err
				}
			}
		}
	}
	return nil
}

func processCategories(tx *gorm.DB, cellVal string, ctg *models.Category, prntID *uint) error {
	catNames := strings.Split(cellVal, " | ")

	// var prntCtg *models.Category
	for idx, catName := range catNames {

		var category models.Category
		// Check if the category already exists
		if tx.Where(&models.Category{Name: catName}).First(&category).RecordNotFound() {
			// If the category doesn't exist, create it
			newCategory := models.Category{Name: catName, Slug: slug.Make(catName), ParentID: prntID}

			// Create the category
			if err := tx.Create(&newCategory).Error; err != nil {

				fmt.Println("Error creating category:", err)
				return err
			}

			// Calculate left and right boundaries
			newCategory.Left, newCategory.Right = utils.CalculateBoundaries(tx, prntID)

			newCategory.Level = idx
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

		prntID = &ctg.ID
	}
	return nil
}

func processPrices(prod *models.Product, tx *gorm.DB, cellVal string, colName string, cities []models.CityGroup) error {
	var err error
	var price models.Price
	var cityGroup models.CityGroup

	priceVal, err := strconv.ParseFloat(cellVal, 64)
	if err != nil {
		log.Fatalf("error while setting new price: %s", err.Error())
		return err
	}

	if idx := utils.BinaryCityGroupSearch(cities, colName); idx >= 0 {
		cityGroup = cities[idx]
	} else {
		return fmt.Errorf("city with name %s not found", colName)
	}

	if tx.Where(&models.Price{CityGroupID: cityGroup.ID, ProductID: prod.ID}).First(&price).RecordNotFound() {
		newPrice := models.Price{CityGroupID: cityGroup.ID, ProductID: prod.ID, Price: priceVal}
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

func processCharacteristics(ctgId uint, prod *models.Product, tx *gorm.DB, val string, charCol string) error {

	char := &models.Characteristic{}
	charVal := &models.CharacteristicValue{}

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
		charVal.Value = val
		if err := tx.Save(charVal).Error; err != nil {
			fmt.Println(err)
			return err
		}
	}
	return nil
}
