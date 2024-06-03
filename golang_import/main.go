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
	"sort"
	"strconv"
	"strings"
	"time"
	"utils"

	"github.com/dgrijalva/jwt-go"
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

	db, err = gorm.Open("postgres", fmt.Sprintf("host=%s port=5432 user=%s dbname=%s password=%s sslmode=disable", dbHost, dbUser, dbName, dbPassword))
	if err != nil {
		log.Fatal("Failed to connect to database: " + err.Error())
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
			fmt.Printf("Table for model %s does not exist, creating...\n", reflect.TypeOf(model).Elem().Name())
			if err := db.AutoMigrate(model).Error; err != nil {
				log.Fatalf("Error while migrate model %s", model)
			} else {
				fmt.Printf("Model %s successfully migrate", model)
			}
		}
	}
}

func main() {
	fmt.Println("Initializing Go server...")
	router := gin.Default()
	router.SetTrustedProxies([]string{"127.0.0.1", "web"})

	authGroup := router.Group("/api/upload")

	authGroup.Use(auth.AuthMiddleware())

	authGroup.PUT("/:filename", processXLSXData)

	router.Run(":8080")
	fmt.Println("Golang server started")
}

func processXLSXData(c *gin.Context) {
	filename := c.Param("filename")
	uploadType := c.Query("type")

	tmpDir := "../media/tmp"
	if err := os.MkdirAll(tmpDir, os.ModePerm); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error. Unable to create directory: " + err.Error()})
		return
	}
	flPth := filepath.Join(tmpDir, filename)

	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if err := c.SaveUploadedFile(file, flPth); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	var ignoredColumns = []string{"TITLE", "IMAGES", "CATEGORIES", "SKU", "PRIORITY", "GROUP", "CHARACTERISTIC"}
	var startTime = time.Now()

	switch uploadType {
	case "PRODUCTS":
		c.JSON(http.StatusOK, gin.H{"message": "Success authorized, products process started..."})
		go func() {
			if err := productsProcess(db, flPth, ignoredColumns); err != nil {
				fmt.Println(err.Error())
				return
			}
			fmt.Printf("Products data processed in %.9fs.\n", time.Since(startTime).Seconds())
			if err := rebuildIndex(); err != nil {
				log.Fatalf(err.Error())
			}
			if err := rebuildCtgTree(); err != nil {
				log.Fatalf(err.Error())
			}
		}()

	case "BRANDS":
		go func() {
			fmt.Println("BRAND data process")
			c.JSON(http.StatusOK, gin.H{"message": "Success authorized, brands process started..."})
			fmt.Printf("BRAND data prodcessed in %.9fs.\n", time.Since(startTime).Seconds())
			if err := rebuildIndex(); err != nil {
				log.Fatalf(err.Error())
			}
		}()
	default:
		c.JSON(http.StatusInternalServerError, gin.H{"error": "unknown upload type: " + uploadType})
	}
}

func productsProcess(db *gorm.DB, filePath string, ignoredColumns []string) error {
	colNms := make(map[string]int)

	r, err := utils.NewReader(filePath, ignoredColumns)
	if err != nil {
		fmt.Printf("error while creating new reader: %s\n", err.Error())
		return err
	}
	defer func() {
		fmt.Println("Products processed, removing tmp file")
		if err := os.Remove(filePath); err != nil {
			fmt.Printf("error while deleting tmp file: %s\n", err.Error())
		} else {
			fmt.Println("tmp file successfully deleted")
		}
		r.Close()
	}()

	var cities []models.CityGroup
	var groups []*models.ProductGroup

	if err := db.Find(&cities).Error; err != nil {
		return fmt.Errorf("failed to get cities: %v", err)
	}

	if err := db.Find(&groups).Error; err != nil {
		return fmt.Errorf("failed to get groups: %v", err)
	}

	sort.Slice(cities, func(i, j int) bool {
		return cities[i].Name < cities[j].Name
	})

	for _, c := range cities {
		r.GetFileReader().CtNms.Cols = append(r.GetFileReader().CtNms.Cols, c.Name)
	}

	rows, err := r.Read()
	if err != nil {
		return err
	}

	for i, col := range r.GetFileReader().Columns {
		colNms[col] = i
	}

	for _, row := range rows[1:] {
		prod := models.Product{}
		ctg := models.Category{}
		prodCtgs := []models.Category{}

		db.Transaction(func(tx *gorm.DB) error {
			if err := processCategories(&prodCtgs, tx, row[colNms["CATEGORIES"]], &ctg); err != nil {
				return err
			}
			if err := processProduct(prodCtgs, tx, row, &prod, &ctg, colNms); err != nil {
				fmt.Printf("Error while processing product: %v\n", err)
				return err
			}
			if err := processProductGroup(prod, groups, tx, row, colNms); err != nil {
				fmt.Printf("Error while processing product group: %v\n", err)
			}
			if err := processRowCells(tx, r, row, colNms, &prod, &ctg, cities); err != nil {
				fmt.Printf("Error while processing row cells: %v\n", err)
			}
			fmt.Printf("Product %s processed\n", prod.Title)
			return nil
		})
	}
	return nil
}

func processProductGroup(prod models.Product, groups []*models.ProductGroup, tx *gorm.DB, row []string, colNms map[string]int) error {
	var group *models.ProductGroup
	idx, ok := colNms["GROUP"]
	if !ok {
		fmt.Println("GROUP column not found")
		return nil
	}

	cellVal, err := utils.GetFromSlice(row, idx)
	if err != nil {
		return err
	}

	grNms := strings.Split(cellVal, ", ")
	for _, nm := range grNms {
		if idx := utils.BinarySearch(
			groups, nm,
			func(a, b interface{}) bool { return a.(*models.ProductGroup).Name < b.(string) },
			func(a, b interface{}) bool { return a.(*models.ProductGroup).Name == b.(string) },
		); idx < 0 {
			continue
		} else {
			tx.Model(&group).Association("Products").Append(prod)
		}
	}

	return nil
}

func processProduct(prodCtgs []models.Category, tx *gorm.DB, row []string, prod *models.Product, ctg *models.Category, colNms map[string]int) error {
	var title string
	var dsc string
	var inStock bool = true // default value for field "in_stock"

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
	}
	if dsc == "" {
		dsc = "Нет описания"
	}

	slg := slug.Make(title)
	if tx.Where(&models.Product{Article: cellVal}).First(&prod).RecordNotFound() {
		newProd := models.Product{Article: cellVal, Title: title, Slug: slg, CategoryID: ctg.ID, BrandID: nil, InStock: inStock}
		if err := tx.Create(&newProd).Error; err != nil {
			return err
		}

		newProd.Slug = fmt.Sprintf("%s-%d", newProd.Slug, newProd.ID)
		if err := tx.Save(&newProd).Error; err != nil {
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
					prod.Priority = uint(priority)
				}
			}
		}
	}
	if !ok || err != nil {
		prod.Priority = 500
	}

	// Set Title & Description
	prod.Description = dsc
	prod.Title = title

	if err = tx.Save(&prod).Error; err != nil {
		return err
	}

	// Set additional categories
	for _, ctg := range prodCtgs {
		if err = tx.Model(&prod).Association("AdditionalCategories").Append(ctg).Error; err != nil {
			fmt.Println("error while add additional category: ", err.Error())
		}
	}

	// Set Images
	if idx, ok := colNms["IMAGES"]; ok {
		cellVal, err = utils.GetFromSlice(row, idx)
		if err != nil {
			return err
		}
		if err = processImages(cellVal, prod, tx); err != nil {
			fmt.Println(err.Error())
		}
	}
	return nil
}

func processImages(cellVal string, prod *models.Product, tx *gorm.DB) error {
	var types = []string{"ORIGINAL", "WATERMARK"}
	imgs := strings.Split(cellVal, " || ")

	if len(imgs) > 0 {
		var bsName string
		for idx, imgUrl := range imgs {
			bsName = strings.Split(filepath.Base(imgUrl), ".")[0]

			response, err := http.Get(imgUrl)
			if err != nil {
				fmt.Printf("error while get image by url %s\n", imgUrl)
				continue
			}
			defer response.Body.Close()

			if idx == 0 {
				types = append(types, "CATALOG", "SEARCH")
			}

			if err := utils.SaveImages(bsName, prod, tx, response, types); err != nil {
				fmt.Println(err.Error())
				continue
			}
		}
	}
	return nil
}

func processCategories(prodCtgs *[]models.Category, tx *gorm.DB, cellVal string, ctg *models.Category) error {
	catNames := strings.Split(cellVal, " || ")
	var prnt *models.Category

	for idx, catName := range catNames[:len(catNames)-1] {
		slg := slug.Make(catName)
		var category models.Category
		if tx.Where(&models.Category{Slug: slg}).First(&category).RecordNotFound() {
			newCategory := models.Category{
				Name:      catName,
				Slug:      slg,
				IsVisible: true,
				TreeID:    1,
				Level:     uint(idx),
			}

			if err := tx.Create(&newCategory).Error; err != nil {
				fmt.Printf("Error creating category: %v\n", err)
				return err
			}
			newCategory.Order = newCategory.ID

			if idx > 0 && prnt != nil {
				prnt.Children = append(prnt.Children, &newCategory)
				if err := tx.Save(prnt).Error; err != nil {
					fmt.Printf("Error saving parent category: %v\n", err)
					return err
				}
			}

			if err := tx.Save(&newCategory).Error; err != nil {
				fmt.Printf("Error saving new category: %v\n", err)
				return err
			}

			*ctg = newCategory
		} else {
			*ctg = category
		}

		*prodCtgs = append(*prodCtgs, *ctg)
		prnt = ctg
	}
	return nil
}

func processPrices(prod *models.Product, tx *gorm.DB, cellVal string, colName string, cities []models.CityGroup) error {
	priceVal, err := strconv.ParseFloat(cellVal, 64)
	if err != nil {
		return err
	}

	var price models.Price
	if idx := utils.BinarySearch(
		cities, colName,
		func(a, b interface{}) bool { return a.(models.CityGroup).Name < b.(string) },
		func(a, b interface{}) bool { return a.(models.CityGroup).Name == b.(string) },
	); idx >= 0 {
		cityGroup := cities[idx]
		if tx.Where(&models.Price{CityGroupID: cityGroup.ID, ProductID: prod.ID}).First(&price).RecordNotFound() {
			newPrice := models.Price{CityGroupID: cityGroup.ID, ProductID: prod.ID, Price: priceVal}
			if err := tx.Create(&newPrice).Error; err != nil {
				fmt.Printf("Error creating price: %v\n", err)
				return err
			}
		} else {
			price.OldPrice = &price.Price
			price.Price = priceVal
			if err := tx.Save(&price).Error; err != nil {
				return err
			}
		}
	} else {
		return fmt.Errorf("city with name %s not found", colName)
	}
	return nil
}

func processCharacteristics(ctgId uint, prod *models.Product, tx *gorm.DB, val string, charCol string) error {
	char := &models.Characteristic{}
	charVal := &models.CharacteristicValue{}

	valSlug := slug.Make(val)
	slug := slug.Make(charCol)
	if tx.Where(&models.Characteristic{Slug: slug}).First(char).RecordNotFound() {
		newChar := models.Characteristic{Name: charCol, CategoryID: ctgId, Slug: slug}
		if err := tx.Create(&newChar).Error; err != nil {
			fmt.Printf("Error creating characteristic: %v\n", err)
			return err
		}
		*char = newChar
	}

	if tx.Where(&models.CharacteristicValue{CharacteristicID: char.ID, ProductID: prod.ID}).First(charVal).RecordNotFound() {
		newCharVal := models.CharacteristicValue{CharacteristicID: char.ID, ProductID: prod.ID, Value: val, Slug: valSlug}
		if err := tx.Create(&newCharVal).Error; err != nil {
			fmt.Printf("Error creating characteristic value: %v\n", err)
			return err
		}
		*charVal = newCharVal
	} else {
		charVal.Value = val
		charVal.Slug = valSlug
		if err := tx.Save(charVal).Error; err != nil {
			return err
		}
	}
	return nil
}
func processRowCells(tx *gorm.DB, r utils.CommonReader, row []string, colNms map[string]int, prod *models.Product, ctg *models.Category, cities []models.CityGroup) error {
	for _, chrCol := range r.GetFileReader().ChrCols.Cols {
		if idx, ok := colNms[chrCol]; ok {
			if chrVal, err := utils.GetFromSlice(row, idx); err == nil && chrVal != "" {
				if err := processCharacteristics(ctg.ID, prod, tx, chrVal, chrCol); err != nil {
					fmt.Printf("Error while processing characteristics: %v\n", err)
				}
			}
		}
	}

	for _, ctCol := range r.GetFileReader().CtNms.Cols {
		if idx, ok := colNms[ctCol]; ok {
			if priceVal, err := utils.GetFromSlice(row, idx); err == nil {
				if err := processPrices(prod, tx, priceVal, ctCol, cities); err != nil {
					fmt.Printf("Error while processing prices: %v\n", err)
				}
			}
		}
	}
	return nil
}

func rebuildIndex() error {
	return sendReqToPyServ("POST", "api/update_index", nil)
}

func rebuildCtgTree() error {
	return sendReqToPyServ("POST", "api/rebuild_category_tree", nil)
}

func GetClaims(c *gin.Context) *jwt.StandardClaims {
	claims, exists := c.Get("Claims")
	if !exists {
		return &jwt.StandardClaims{}
	}
	return claims.(*jwt.StandardClaims)
}
func sendReqToPyServ(method, viewName string, body *bytes.Buffer) error {
	if body == nil {
		body = bytes.NewBuffer([]byte(""))
	}

	client := &http.Client{}
	url := fmt.Sprintf("http://web:8000/%s/", viewName)
	req, err := http.NewRequest(method, url, body)
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Ошибка выполнения запроса %s: %v", url, err)
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 200 && 400 > resp.StatusCode {
		log.Printf("Запрос успешно %s выполнен: %s", url, resp.Status)
	} else {
		log.Printf("Не удалось выполнить запрос %s. Статус: %v\n", url, resp.StatusCode)
	}

	return nil
}
