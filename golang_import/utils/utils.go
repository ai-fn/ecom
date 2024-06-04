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
	"models"
	"os"
	"path/filepath"
	"reflect"
	"strconv"

	"github.com/google/uuid"
	"github.com/jinzhu/gorm"
	"github.com/nfnt/resize"
	"github.com/xuri/excelize/v2"
	_ "golang.org/x/image/webp"
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
	dfltVals["CATALOG"] = []string{"960", "540"}
	dfltVals["WATERMARK"] = []string{"1280", "720"}
	dfltVals["SEARCH"] = []string{"68", "38"}
	dfltVals["WT_MARK"] = []string{"68", "38"}

	if size, exists := dfltVals[imgType]; exists {
		return ConvertStrToUint(size...)
	}

	return nil, fmt.Errorf("provided wrong image type: %s", imgType)
}

func SaveImages(bsName, url string, prod *models.Product, tx *gorm.DB, imgTypes []string) error {
	var catalogPath = os.Getenv("CATALOG_PATH")
	if catalogPath == "" {
		catalogPath = "catalog/products/"
	}

	format := filepath.Ext(url)

	baseMediaPath := os.Getenv("MEDIA_PATH")
	if baseMediaPath == "" {
		baseMediaPath = "../media/"
	}

	imgFl, err := os.Open(baseMediaPath + catalogPath + url)
	if err != nil {
		return err
	}
	defer imgFl.Close()

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
		img, err = png.Decode(imgFl)
	case ".jpg":
		img, err = jpeg.Decode(imgFl)
	default:
		img, _, err = image.Decode(imgFl)
	}

	if err != nil {
		return err
	}

	setThumbImage(prod, img)

	for _, imgType := range imgTypes {
		if !tx.Where(&models.ProductImage{Name: fmt.Sprintf("%s_%s", imgType, bsName)}).First(&models.ProductImage{}).RecordNotFound() {
			continue
		}

		flName := fmt.Sprintf("%s_%s", imgType, fileName)
		pth := catalogPath + flName + ".webp"
		filePath := baseMediaPath + pth

		var err error
		if imgType == "ORIGINAL" {
			prod.OriginalImage = filePath
		} else {
			err = processAndSaveImage(img, webpBuffer, filePath, wtrmkPath, imgType, bsName, prod, tx)
		}

		if err != nil {
			return err
		}
		webpBuffer.Reset()
	}

	if err := tx.Save(prod).Error; err != nil {
		return err
	}
	return nil
}

func processAndSaveImage(img image.Image, webpBuffer bytes.Buffer, filePath, wtrmkPath, imgType, bsName string, prod *models.Product, tx *gorm.DB) error {
	size, err := getSize(imgType)
	if err != nil {
		fmt.Printf("error while get size: %s\n", err)
		return err
	}
	img = resizeImg(img, size)

	if imgType == "WATERMARK" {
		img, err = watermarkImg(img, wtrmkPath)
		if err != nil {
			fmt.Printf("error while watermark image: %v\n", err)
			return err
		}

		newProdImage := &models.ProductImage{
			Image:     filePath,
			ProductID: prod.ID,
			Name:      fmt.Sprintf("%s_%s", imgType, bsName),
		}

		if err := setThumbImage(newProdImage, img); err != nil {
			fmt.Printf("error while set thumb image: %v\n", err)
			return err
		}
		if err := tx.Create(newProdImage).Error; err != nil {
			return err
		}
	} else {
		switch imgType {
		case "CATALOG":
			prod.CatalogImage = filePath
		case "SEARCH":
			prod.SearchImage = filePath
		}
	}

	if err := saveImageFile(webpBuffer, img, filePath); err != nil {
		fmt.Printf("error while save resized image: %v\n", err)
		return err
	}

	return nil
}

func resizeImg(img image.Image, size []uint) image.Image {

	targetRatio := uint(4 / 3)
	targetHeight, targetWidth := size[1]/targetRatio, int(size[0]/targetRatio)

	resized := resize.Resize(0, targetHeight, img, resize.Lanczos3)
	resultWidth := resized.Bounds().Dx()

	if resultWidth < targetWidth {
		resized = extendToWidth(resized, targetWidth)
	} else if resultWidth > targetWidth {

		// Cropp image
		xOffset := (resultWidth - targetWidth) / 2
		resized = resized.(interface {
			SubImage(r image.Rectangle) image.Image
		}).SubImage(image.Rect(xOffset, 0, xOffset+targetWidth, int(targetHeight)))
	}
	return resized
}

func saveImageFile(webpBuffer bytes.Buffer, img image.Image, filePath string) error {
	err := png.Encode(&webpBuffer, img)
	if err != nil {
		fmt.Printf("error while encode image as webp: %s\n", err)
		return err
	}

	err = os.WriteFile(filePath, webpBuffer.Bytes(), 0644)
	if err != nil {
		fmt.Printf("error while write file: %s\n", err)
		return err
	}

	return nil
}

func setThumbImage(obj interface{}, img image.Image) (err error) {
	var thumbBuff bytes.Buffer
	var attributeName = "ThumbModel"
	thumb_img := resize.Resize(0, 8, img, resize.Lanczos2)

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

func watermarkImg(origImg image.Image, wtmrkPath string) (image.Image, error) {
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

	wtrmkImg = resize.Resize(0, wtrmrkSize[0], wtrmkImg, resize.Lanczos3)

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

	position := image.Pt(origBounds.Max.X-wtrmkBounds.Dx()-margin, origBounds.Max.Y-wtrmkBounds.Dy()-margin)
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

func extendToWidth(origImg image.Image, width int) image.Image {
	origBounds := origImg.Bounds()

	newImg := image.NewRGBA(image.Rect(0, 0, width, origBounds.Dy()))

	dstPt := image.Pt(
		(origBounds.Dx()-newImg.Bounds().Dx())/2,
		0,
	)
	draw.Draw(newImg, newImg.Bounds(), origImg, dstPt, draw.Over)

	return newImg
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
