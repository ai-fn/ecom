package main

import (
	"auth"
	"bytes"
	"fmt"
	"log"
	"models"
	"net/http"
	"os"
	"path/filepath"
	"reflect"
	"strconv"
	"strings"
	"time"
	"utils"

	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	_ "main/docs"

	"github.com/gosimple/slug"
	"github.com/jinzhu/gorm"
	_ "github.com/swaggo/http-swagger"
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
	connStr := fmt.Sprintf("host=%s port=5432 user=%s dbname=%s password=%s sslmode=disable", dbHost, dbUser, dbName, dbPassword)

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

// @title Products Import API
// @version 1.12.2
// @description API for product imoprt
func main() {
	fmt.Println("Initializing golang server...")
	router := gin.Default()

	authGroup := router.Group("/api/upload")

	authGroup.Use(auth.AuthMiddleware())

	authGroup.PUT("/:filename", processXLSXData)

	// Swagger handler
	router.GET("/api/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	router.Run(":8080")
	fmt.Println("Golang server started")
}

// @Summary Загрузка файла товаров
// @Description Загрузка файла с товарами для импорта
// @ID uploadFile
// @Accept multipart/form-data
// @Produce json
// @Param filename path string true "Имя файла"
// @Param type query string true "Тип данных для импорта (PRODUCTS, BRANDS)"
// @Success 200 {string} string "OK"
// @Router /api/upload/{filename} [PUT]
// @Tags Import
// @Param Authorization header string true "Insert your access token" default(Bearer <Add access token here>)
func processXLSXData(c *gin.Context) {

	filename := c.Param("filename")

	// Create a bytes buffer to store the file content
	var buf bytes.Buffer

	_, err := buf.ReadFrom(c.Request.Body)
	if err != nil {
		c.JSON(500, gin.H{"error": "Internal server error. Unable to read file content." + err.Error()})
		return
	}

	if buf.Len() == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "File data is required."})
		return
	}

	// Retrieve upload type from query parameters
	uploadType := c.Query("type")

	tmpDir := "../media/tmp"
	if err = os.MkdirAll(tmpDir, os.ModePerm); err != nil {
		c.JSON(500, gin.H{"error": "Internal server error. Unable to create directory: " + err.Error()})
		return
	}
	flPth := filepath.Join(tmpDir, filename)
	out, err := os.Create(flPth)
	if err != nil {
		c.JSON(500, gin.H{"error": "Internal server error. Unable to create file: " + err.Error()})
		return
	}

	defer out.Close()

	_, err = buf.WriteTo(out)
	if err != nil {
		c.JSON(500, gin.H{"error": "Internal server error. Unable to save file: " + err.Error()})
		return
	}

	// Parse CSV data and process accordingly based on uploadType
	var ignoredColumns = []string{"TITLE", "IMAGES", "CATEGORIES", "SKU", "PRIORITY"}
	var startTime = time.Now()

	switch uploadType {
	case "PRODUCTS":
		// go func() {
		err := productsProcess(db, flPth, ignoredColumns)
		if err != nil {
			log.Fatal(err)
			return
		}
		fmt.Printf("Products data processed in %.9fs.\n", time.Since(startTime).Seconds())
		c.JSON(http.StatusOK, gin.H{"message": "Success authorized, products process started..."})
		// }()

	case "BRANDS":
		go func() {
			fmt.Println("BRAND data process")
			c.JSON(http.StatusOK, gin.H{"message": "Success authorized, brands process started..."})

			// Process brand data
			// Your logic for processing brands here
			fmt.Printf("BRAND data prodcessed in %.9fs.\n", time.Since(startTime).Seconds())
		}()
	default:
		c.String(500, fmt.Sprintf("unknown upload type: %s", uploadType))
	}
}

func productsProcess(db *gorm.DB, filePath string, ignoredColumns []string) error {

	colNms := make(map[string]int, 0)
	cityCols := make([]string, 0)
	chrCols := &models.Columns{Cols: []string{}}

	r, err := utils.NewReader(filePath, ignoredColumns)
	if err != nil {
		log.Fatalf("error while create new reader: %s", err.Error())
		return err
	}

	defer func() {
		r.Close()
		fmt.Println("Products processed, remove tmp file")
		if err := os.Remove(filePath); err == nil {
			fmt.Println("tmp file successfully deleted")
		} else {
			fmt.Println("tmp file not found, exit.")
		}
	}()

	// Select cities from db
	var cities []models.City
	result := db.Find(&cities)
	if result.Error != nil {
		return fmt.Errorf("failed to get cities: " + result.Error.Error())
	}

	// Insert city names into slice
	for _, c := range cities {
		r.GetFileReader().CtNms.Cols = append(r.GetFileReader().CtNms.Cols, c.Name)
	}

	// Iterate over each row, start from second, in the sheet
	var colName string

	var rIdx = 0
	for {
		row, err := r.Read()
		if err != nil {
			break
		}
		rIdx++
		if rIdx == 1 {
			continue
		}

		idx := 0
		prod := models.Product{}
		ctg := models.Category{}

		idx = colNms["CATEGORIES"]

		// Initializer Transaction
		db.Transaction(func(tx *gorm.DB) error {

			var err error
			// Process categories
			if err = processCategories(db, row[idx], &ctg); err != nil {
				return nil
			}

			processProduct(db, row, &prod, &ctg, colNms)

			// Process row's cells
			for _, colName := range chrCols.Cols {
				if err = processCharacteristics(ctg.ID, &prod, db, row[colNms[colName]], colName); err != nil {
					return err
				}
			}
			for _, colName = range cityCols {
				if err = processPrices(&prod, db, row[colNms[colName]], colName, cities); err != nil {
					return err
				}
			}
			return nil
		})
		fmt.Printf("Product %s processed\n", prod.Title)
	}
	return nil
}

func processProduct(tx *gorm.DB, row []string, prod *models.Product, ctg *models.Category, colNms map[string]int) error {
	var cellVal = row[colNms["SKU"]]
	title := row[colNms["TITLE"]]
	fmt.Println(cellVal, title)
	if tx.Where(&models.Product{Article: cellVal}).First(&prod).RecordNotFound() {
		newProd := models.Product{Article: cellVal, Slug: slug.Make(title), CategoryID: ctg.ID, BrandID: nil}
		if err := tx.Create(&newProd).Error; err != nil {
			// Print error and return
			return err
		}
		*prod = newProd
	}

	// Set Priority
	cellVal = row[colNms["PRIORITY"]]
	if cellVal != "" {
		priority, err := strconv.ParseFloat(cellVal, 32)
		if err != nil {
			return fmt.Errorf("error while parse priority: %s", err.Error())
		}
		prod.Priority = int(priority)
	}

	if err := tx.Save(&prod).Error; err != nil {
		return err
	}

	// Set Images
	cellVal = row[colNms["IMAGES"]]
	imgs := strings.Split(cellVal, ",")

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

func processCategories(tx *gorm.DB, cellVal string, ctg *models.Category) error {
	catNames := strings.Split(cellVal, " | ")

	var prntID *uint // Initialize parentID
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

func processPrices(prod *models.Product, tx *gorm.DB, cellVal string, colName string, cities []models.City) error {
	var city models.City
	var price models.Price
	var err error

	priceVal, err := strconv.ParseFloat(cellVal, 64)
	if err != nil {
		log.Fatalf("error while setting new price: %s", err.Error())
		return err
	}

	if find, err := utils.FindByField(cities, "Name", colName); err != nil {
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
