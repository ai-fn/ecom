package utils

import (
	"bytes"
	"encoding/base64"
	"encoding/csv"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/jpeg"
	"image/png"
	"io"
	"models"
	"net/http"
	"os"
	"path/filepath"
	"reflect"
	"strconv"

	"github.com/google/uuid"
	"github.com/jinzhu/gorm"
	"github.com/nfnt/resize"
	"github.com/xuri/excelize/v2"
)

type CommonReader interface {
	openFile(fp string) error
	Read() ([][]string, error)
	Close() error
	GetFileReader() *FileReader
}

type FileReaderInterface interface {
	SetColumns([]string) error
}

type FileReader struct {
	CtNms          *models.Columns
	ChrCols        *models.Columns
	IgnoredColumns *models.Columns
	Columns        []string
	FilePath       string
}

type CSVReader struct {
	FileReader    *FileReader
	File          *os.File
	DefaultReader *csv.Reader
}

type XLSXReader struct {
	FileReader *FileReader
	File       *excelize.File
	Rows       *excelize.Rows
}

func (r *CSVReader) GetFileReader() *FileReader {
	return r.FileReader
}

func (r *XLSXReader) GetFileReader() *FileReader {
	return r.FileReader
}

func (r *CSVReader) openFile(fp string) error {
	file, err := os.Open(fp)
	if err != nil {
		return err
	}

	r.File = file
	r.DefaultReader = csv.NewReader(file)
	return nil
}

func (r *CSVReader) Read() (rows [][]string, err error) {
	rows, err = r.DefaultReader.ReadAll()
	if err != nil {
		return
	}

	if err = r.FileReader.SetColumns(rows[0]); err != nil {
		return
	}
	return
}

func (r *CSVReader) Close() error {
	if r.File != nil {
		if err := r.File.Close(); err != nil {
			return err
		}
	}
	return nil
}

func (r *FileReader) SetColumns(row []string) error {
	r.Columns = row

	for _, cellVal := range r.Columns {
		if !r.IgnoredColumns.Contains(cellVal) {

			if r.CtNms.Contains(cellVal) {
				r.CtNms.Cols = append(r.CtNms.Cols, cellVal)
				continue
			}
			r.ChrCols.Cols = append(r.ChrCols.Cols, cellVal)
		}
	}

	return nil
}

func (r *FileReader) ColsIsValid() error {
	var cols = models.Columns{Cols: r.Columns}
	for _, el := range r.IgnoredColumns.Cols {

		if !cols.Contains(el) {
			return fmt.Errorf("не все обязательные поля найдены в документе: %s", el)
		}
	}
	return nil
}

func (r *XLSXReader) openFile(fp string) error {
	file, err := excelize.OpenFile(fp)
	if err != nil {
		return err
	}
	r.File = file
	if rows, err := file.Rows(file.GetSheetList()[0]); err != nil { // Read only first sheet
		return err
	} else {
		r.Rows = rows
	}

	return nil
}

func (r *XLSXReader) Read() (rows [][]string, err error) {
	if r.Rows.Next() {
		rows, err = r.File.GetRows(r.File.GetSheetName(0))
		if err != nil {
			return
		}
		r.FileReader.SetColumns(rows[0])
	}
	return
}

func (r *XLSXReader) Close() error {
	if r.File != nil {
		if err := r.File.Close(); err != nil {
			return err
		}
	}
	return nil
}

func NewReader(fp string, ignoredColumns []string) (CommonReader, error) {
	var cmnReader CommonReader
	format := filepath.Ext(fp)
	reader := &FileReader{
		FilePath:       fp,
		IgnoredColumns: &models.Columns{Cols: ignoredColumns},
		CtNms:          &models.Columns{},
		ChrCols:        &models.Columns{},
	}
	switch format {
	case ".xlsx":
		cmnReader = &XLSXReader{
			FileReader: reader,
		}
	case ".csv":
		cmnReader = &CSVReader{
			FileReader: reader,
		}
	default:
		return nil, fmt.Errorf("unexpected file format: %s", format)
	}

	if err := cmnReader.openFile(fp); err != nil {
		return nil, err
	}
	return cmnReader, nil
}

func ConvertStrToUint(s ...string) ([]uint, error) {
	if s == nil {
		return nil, fmt.Errorf("string params is required")
	}
	res := make([]uint, len(s))
	for idx, el := range s {
		val, err := strconv.ParseUint(el, 10, 64)
		if err != nil {
			fmt.Printf("cannot parse %s to int\n", el)
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

	width := os.Getenv(fmt.Sprintf("PRODUCT_%s_IMAGE_WIDTH", imgType))
	height := os.Getenv(fmt.Sprintf("PRODUCT_%s_IMAGE_HEIGHT", imgType))
	if width == "" || height == "" {
		if size, exists := dfltVals[imgType]; exists {
			return ConvertStrToUint(size[0], size[1])
		}
		return nil, fmt.Errorf("provided wrong image type: %s", imgType)
	}
	return ConvertStrToUint(width, height)
}

func SaveImages(bsName string, prod *models.Product, tx *gorm.DB, r *http.Response, imgTypes []string) error {
	var catalogPath = os.Getenv("CATALOG_PATH")
	if catalogPath == "" {
		catalogPath = "catalog/products/"
	}

	data, err := io.ReadAll(r.Body)
	if err != nil {
		fmt.Printf("error while read response body: %s\n", err.Error())
		return err
	}

	format := filepath.Ext(r.Request.URL.Path)

	baseMediaPath := os.Getenv("MEDIA_PATH")
	if baseMediaPath == "" {
		baseMediaPath = "../media/"
	}

	if _, err := os.Stat(baseMediaPath + catalogPath); os.IsNotExist(err) {
		fmt.Printf("Media path is not exist: %s, creating...\n", baseMediaPath+catalogPath)

		if err = os.MkdirAll(baseMediaPath+catalogPath, os.ModePerm); err != nil {
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

	switch format {
	case ".png":
		img, err = png.Decode(bytes.NewReader(data))
	case ".jpg":
		img, err = jpeg.Decode(bytes.NewReader(data))
	default:
		img, _, err = image.Decode(bytes.NewReader(data))
	}

	if err != nil {
		return err
	}

	if err = setThumbImage(prod, img); err != nil {
		fmt.Println(err)
	} else {
		if err = tx.Save(&prod).Error; err != nil {
			fmt.Println(err.Error())
			return err
		}
	}

	for _, imgType := range imgTypes {
		if !tx.Where(&models.ProductImage{Name: fmt.Sprintf("%s_%s", imgType, bsName)}).First(&models.ProductImage{}).RecordNotFound() {
			continue
		}

		size, err := getSize(imgType)
		if err != nil {
			fmt.Printf("error while get size: %s\n", err)
			continue
		}

		flName := fmt.Sprintf("%s_%s", imgType, fileName)

		resized := resize.Resize(size[1]*16/9, size[1], img, resize.Lanczos3)

		if imgType == "WATERMARK" {
			resized, err = WatermarkImg(resized, wtrmkPath)
			if err != nil {
				fmt.Printf("error while watermark image: %s\n", err.Error())
				continue
			}
		}

		err = png.Encode(&webpBuffer, resized)
		if err != nil {
			fmt.Printf("error while encode image as webp: %s\n", err)
			continue
		}

		filePath := baseMediaPath + catalogPath + flName + ".webp"
		err = os.WriteFile(filePath, webpBuffer.Bytes(), 0644)
		if err != nil {
			fmt.Printf("error while write file: %s\n", err)
			continue
		}

		webpBuffer.Reset()
		pth := catalogPath + flName + ".webp"
		switch imgType {
		case "WATERMARK":
			var newProdImage = &models.ProductImage{
				Image:     pth,
				ProductID: prod.ID,
				Name:      fmt.Sprintf("%s_%s", imgType, bsName),
			}
			if err = setThumbImage(newProdImage, resized); err != nil {
				fmt.Println(err)
				continue
			}
			err = tx.Create(&newProdImage).Error

		case "CATALOG":
			prod.CatalogImage = pth
			err = tx.Save(&prod).Error

		case "SEARCH":
			prod.SearchImage = pth
			err = tx.Save(&prod).Error

		default:
			fmt.Println("Unknown image type")
		}

		if err != nil {
			return err
		}
	}
	return nil
}

func setThumbImage(obj interface{}, img image.Image) (err error) {
	var thumbBuff bytes.Buffer
	var attributeName = "ThumbModel"
	thumb_img := resize.Resize(8, 8, img, resize.Lanczos2)

	if err = jpeg.Encode(&thumbBuff, thumb_img, &jpeg.Options{}); err != nil {
		err = fmt.Errorf("error while encode image into thumb buffer: %s", err.Error())
		return
	} else {
		val := reflect.ValueOf(obj).Elem()
		field := val.FieldByName(attributeName)
		if !field.IsValid() {
			err = fmt.Errorf("attribute '%s' not found", attributeName)
			return
		}

		if !field.CanSet() {
			err = fmt.Errorf("cannot set attribute '%s'", attributeName)
			return
		}

		field.Set(reflect.ValueOf(models.ThumbModel{Thumb: base64.RawStdEncoding.EncodeToString(thumbBuff.Bytes())}))
	}
	return
}

func WatermarkImg(origImg image.Image, wtmrkPath string) (image.Image, error) {
	wtrmkFile, err := os.Open(wtmrkPath)
	if err != nil {
		return nil, err
	}
	defer wtrmkFile.Close()

	wtrmkImg, _, err := image.Decode(wtrmkFile)
	if err != nil {
		return nil, err
	}

	wtrmrkSize, err := getSize("WT_MARK")
	if err != nil {
		return nil, err
	}

	wtrmkImg = resize.Resize(uint(wtrmrkSize[1]*16/9), uint(wtrmrkSize[1]), wtrmkImg, resize.Lanczos3)

	opacity, err := getEnvInt("WATERMARK_OPACITY", 80)
	if err != nil {
		return nil, err
	}

	opacityColor := color.Alpha{A: uint8(opacity)}

	origBounds := origImg.Bounds()
	wtrmkBounds := wtrmkImg.Bounds()

	margin, err := getEnvInt("WATERMARK_MARGIN", 30)
	if err != nil {
		fmt.Println("Invalid watermark margin, set default (30)")
		margin = 30
	}

	position := image.Pt(origBounds.Dx()-wtrmkBounds.Dx()-margin, origBounds.Dy()-wtrmkBounds.Dy()-margin)
	drawImg := image.NewRGBA(origBounds)

	draw.Draw(drawImg, origBounds, origImg, origBounds.Min, draw.Src)

	draw.DrawMask(drawImg, wtrmkBounds.Add(position), wtrmkImg, wtrmkBounds.Min, &image.Uniform{C: opacityColor}, image.Point{}, draw.Over)

	return drawImg, nil
}

func parseInt(s string) (int, error) {
	var result int
	var negative bool
	var startIndex int

	if s[0] == '-' {
		negative = true
		startIndex = 1
	}

	for i := startIndex; i < len(s); i++ {
		char := s[i]
		if char < '0' || char > '9' {
			return 0, fmt.Errorf("invalid input: each character must be from 0 to 9")
		}
		digit := int(char - '0')
		result = result*10 + digit
	}

	if negative {
		result = -result
	}

	return result, nil
}

func GetFromSlice(slice []string, idx int) (string, error) {
	if idx < 0 || len(slice) <= idx {
		return "", fmt.Errorf("index out of range: %d of %d", idx, len(slice))
	}

	return slice[idx], nil
}

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

func BinarySearch(arr interface{}, pattern interface{}, less func(a, b interface{}) bool, equal func(a, b interface{}) bool) int {
	v := reflect.ValueOf(arr)
	if v.Kind() != reflect.Slice {
		fmt.Println("arr is not a slice")
		return -1
	}

	low := 0
	high := v.Len() - 1

	for low <= high {
		mid := (low + high) / 2
		midVal := v.Index(mid).Interface()

		if equal(midVal, pattern) {
			return mid
		}

		if less(midVal, pattern) {
			low = mid + 1
		} else {
			high = mid - 1
		}
	}
	return -1
}

func getEnvInt(key string, defaultValue int) (int, error) {
	valueStr := os.Getenv(key)
	if valueStr == "" {
		return defaultValue, nil
	}
	return parseInt(valueStr)
}
