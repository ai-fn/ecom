package utils

import (
	"bytes"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/jpeg"
	"image/png"
	"io"
	"log"
	"models"
	"net/http"
	"os"
	"path/filepath"
	"reflect"
	"strconv"

	"github.com/google/uuid"
	"github.com/jinzhu/gorm"
	"github.com/nfnt/resize"
)

func ConvertStrToUint(s ...string) ([]uint, error) {
	if s == nil {
		return nil, fmt.Errorf("string params is required")
	}
	res := make([]uint, len(s))
	for idx, el := range s {
		val, err := strconv.ParseUint(el, 10, 64)
		if err != nil {
			log.Fatalf("cannot parse %s to int", el)
		}
		res[idx] = uint(val)
	}
	return res, nil
}

func getSize(imgType string) ([]uint, error) {
	dfltVals := make(map[string][]string)
	dfltVals["CATALOG"] = []string{"500", "500"}
	dfltVals["WATERMARK"] = []string{"1280", "720"}
	dfltVals["SEARCH"] = []string{"42", "50"}
	dfltVals["WT_MARK"] = []string{"42", "50"}

	width := os.Getenv(fmt.Sprintf("%s_IMAGE_WIDTH", imgType))
	height := os.Getenv(fmt.Sprintf("%s_IMAGE_HEIGHT", imgType))
	if width == "" || height == "" {
		if size, exists := dfltVals[imgType]; exists {
			return ConvertStrToUint(size[0], size[1])
		}
		return ConvertStrToUint(width, height)
	}
	return nil, fmt.Errorf("provided wrong image type: %s", imgType)
}

func SaveImages(prod *models.Product, tx *gorm.DB, r *http.Response, imgTypes []string) error {
	var catalogPath = os.Getenv("CATALOG_PATH")
	if catalogPath == "" {
		catalogPath = "catalog/products/"
	}

	data, err := io.ReadAll(r.Body)
	if err != nil {
		log.Fatalf("error while read response body: %s", err.Error())
		return err
	}

	format := filepath.Ext(r.Request.URL.Path)

	baseMediaPath := os.Getenv("MEDIA_PATH")
	if baseMediaPath == "" {
		baseMediaPath = "../media/"
	}

	// Check or create base media path
	if _, err := os.Stat(baseMediaPath + catalogPath); os.IsNotExist(err) {
		fmt.Printf("Media path is not exist: %s, creating...\n", baseMediaPath+catalogPath)

		if err = os.MkdirAll(baseMediaPath+catalogPath, os.ModePerm); err != nil {
			log.Fatalf("error while make media dirs: %s", err.Error())
			return err
		}
	}

	wtrmkPath := os.Getenv("WATERMARK_PATH")
	if wtrmkPath == "" {
		wtrmkPath = "watermarks/KM_Logotype_2048.png"
	}
	wtrmkPath = "../" + wtrmkPath

	var webpBuffer bytes.Buffer
	var img image.Image
	var fileName string = fmt.Sprintf("image-%s", uuid.New())

	// Decode images in different formats
	switch format {
	case ".png":
		img, err = png.Decode(bytes.NewReader(data))
	case ".jpg":
		img, err = jpeg.Decode(bytes.NewReader(data))
	default:
		img, _, err = image.Decode(bytes.NewReader(data))
	}
	if err != nil {
		log.Fatalf("error while image decode: %s", err)
		fmt.Println(err.Error())
		return err
	}

	for _, imgType := range imgTypes {
		size, err := getSize(imgType)
		if err != nil {
			log.Fatalf("error while get size: %s", err)
			fmt.Println(err.Error())
			continue
		}

		flName := fmt.Sprintf("%s_%s", imgType, fileName)

		resized := resize.Resize(size[0], size[1], img, resize.Lanczos3)

		if imgType == "WATERMARK" {
			err = WatermarkImg(resized, wtrmkPath)
			if err != nil {
				log.Fatalf("error while watermark image: %s", err.Error())
				fmt.Println(err.Error())
				continue
			}
		}

		// Encode the image as WebP
		err = png.Encode(&webpBuffer, resized)
		if err != nil {
			log.Fatalf("error while encode image as webp: %s", err)
			fmt.Println(err.Error())
			continue
		}

		// Save image
		err = os.WriteFile(baseMediaPath+catalogPath+flName+".webp", webpBuffer.Bytes(), 0644)
		if err != nil {
			log.Fatalf("error while write file: %s", err)
			fmt.Println(err.Error())
			continue
		}

		webpBuffer.Reset()
		if err := tx.Create(&models.ProductImage{Image: catalogPath + flName + ".webp", ProductID: prod.ID}).Error; err != nil {
			return err
		}
	}

	return nil
}

func WatermarkImg(origImg image.Image, wtmrkPath string) error {
	wtrmkFile, err := os.Open(wtmrkPath)
	if err != nil {
		return err
	}
	defer wtrmkFile.Close()

	wtrmkImg, _, err := image.Decode(wtrmkFile)
	if err != nil {
		return err
	}

	wtrmrkSize, err := getSize("WT_MARK")
	if err != nil {
		return err
	}

	wtrmkImg = resize.Resize(wtrmrkSize[0], wtrmrkSize[1], wtrmkImg, resize.Lanczos3)
	strOpacity := os.Getenv("WATERMARK_OPACITY")
	if strOpacity == "" {
		strOpacity = "60"
	}

	opacity, err := parseInt(strOpacity)
	if err != nil {
		return err
	}

	mask := image.NewUniform(&color.Alpha{uint8(255 * opacity / 100)}) // Set provided opacity

	// Calculate the position to place the watermark
	origBounds := origImg.Bounds()
	wtrmkBounds := wtrmkImg.Bounds()

	// Get watermark margin or set default
	strMargin := os.Getenv("WATERMARK_MARGIN")
	if strMargin == "" {
		strMargin = "30"
	}
	margin, err := parseInt(strMargin)
	if err != nil {
		fmt.Println("Invalid watermark margin, set default (30)")
		margin = 30
	}

	position := image.Pt(origBounds.Dx()-wtrmkBounds.Dx()-margin, origBounds.Dy()-wtrmkBounds.Dy()-margin)

	// Draw watermark onto the original image
	draw.DrawMask(origImg.(draw.Image), wtrmkBounds.Add(position), wtrmkImg, image.Point{}, mask, image.Point{}, draw.Over)

	return nil
}

func parseInt(s string) (int, error) {
	var result int
	var negative bool

	for i, char := range s {
		if i == 0 && char == '-' {
			negative = true
			continue
		}
		if char < '0' || char > '9' {
			return 0, fmt.Errorf("invalid input: each num must be from 0 to 9")
		}
		digit := int(char - '0')
		result = result*10 + digit
	}

	if negative {
		result = -result
	}

	return result, nil
}

// findByField finds an element in the slice of any structs by the provided field value.
func FindByField(slice interface{}, field string, value interface{}) (interface{}, error) {
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
func CalculateBoundaries(db *gorm.DB, prntID *uint) (int, int) {
	if prntID == nil || (*prntID) == 0 {
		// If the node has no parent, set lft to 1 and rght to 2
		return 1, 2
	}

	// Find the maximum right boundary of the parent's children
	maxRght := db.Model(&models.Category{}).
		Where("parent_id = ?", prntID).
		Select("MAX(rght)").
		Row()

	var maxRghtValue int
	if err := maxRght.Scan(&maxRghtValue); err != nil {
		// Handle error
		log.Fatalf(err.Error())
		return 0, 0
	}

	// Set lft to the maximum right boundary of the parent's children
	lft := maxRghtValue + 1
	// Set rght to lft + 1
	rght := lft + 1
	return lft, rght
}
