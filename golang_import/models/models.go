package models

import (
	"slices"
	"time"

	_ "github.com/jinzhu/gorm/dialects/postgres"
)

type Columns struct {
	Cols []string
}

type Login struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type CustomUser struct {
	CustomModel
	Username   string `gorm:"column:username;unique"`
	Email      string `gorm:"column:email;unique"`
	Password   string `gorm:"column:password"`
	Phone      string `gorm:"column:phone;unique"`
	CityID     uint   `gorm:"column:city_id"`
	City       City   `gorm:"foreignkey:CityID"`
	Region     string `gorm:"column:region"`
	District   string `gorm:"column:district"`
	CityName   string `gorm:"column:city_name"`
	Street     string `gorm:"column:street"`
	House      string `gorm:"column:house"`
	IsCustomer bool   `gorm:"column:is_customer"`
	MiddleName string `gorm:"column:middle_name"`
}

type CustomModel struct {
	ID        uint `gorm:"primary_key"`
	CreatedAt time.Time
	UpdatedAt time.Time
}

type BaseModel struct {
	DeletedAt *time.Time `sql:"index"`
}

type Category struct {
	CustomModel
	BaseModel
	Name      string      `gorm:"column:name"`
	Slug      string      `gorm:"column:slug"`
	ParentID  *uint       `gorm:"column:parent_id"`
	Icon      string      `gorm:"column:icon;type:varchar(255)"`
	Image     string      `gorm:"column:image;type:varchar(255)"`
	IsVisible bool        `gorm:"column:is_visible"`
	IsPopular bool        `gorm:"column:is_popular"`
	Order     int         `gorm:"column:order"`
	Parent    *Category   `gorm:"foreignKey:ParentID"`
	Children  []*Category `gorm:"foreignKey:ParentID"`
	Left      int         `gorm:"column:lft"`
	Right     int         `gorm:"column:rght"`
	TreeID    int         `gorm:"column:tree_id"`
	Level     int         `gorm:"column:level"`
}

type Product struct {
	CustomModel
	BaseModel
	CategoryID           uint        `gorm:"column:category_id"`
	BrandID              *uint       `gorm:"column:brand_id"`
	Title                string      `gorm:"column:title"`
	Description          string      `gorm:"column:description;type:text"`
	Image                string      `gorm:"column:image;type:varchar(255)"`
	CatalogImage         string      `gorm:"column:catalog_image;type:varchar(255)"`
	SearchImage          string      `gorm:"column:search_image;type:varchar(255)"`
	Slug                 string      `gorm:"column:slug;unique"`
	InStock              bool        `gorm:"column:in_stock"`
	IsPopular            bool        `gorm:"column:is_popular"`
	Priority             int         `gorm:"column:priority"`
	Category             Category    `gorm:"foreignKey:CategoryID"`
	AdditionalCategories []*Category `gorm:"many2many:product_additional_categories"`
	Brand                *Brand      `gorm:"foreignKey:BrandID"`
}

type Brand struct {
	CustomModel
	Name  string `gorm:"column:name"`
	Icon  string `gorm:"column:icon;type:varchar(255)"`
	Slug  string `gorm:"column:slug;unique"`
	Order int    `gorm:"column:order"`
}

type Price struct {
	CustomModel
	BaseModel
	ProductID uint     `gorm:"column:product_id"`
	CityID    uint     `gorm:"column:city_id"`
	Price     float64  `gorm:"column:price;type:decimal(10,2)"`
	OldPrice  *float64 `gorm:"column:old_price;type:decimal(10,2)"`
}

type Characteristic struct {
	CustomModel
	BaseModel
	Name       string `gorm:"column:name;unique"`
	CategoryID uint   `gorm:"column:category_id"`
}

type CharacteristicValue struct {
	CustomModel
	BaseModel
	ProductID        uint   `gorm:"column:product_id"`
	CharacteristicID uint   `gorm:"column:characteristic_id"`
	Value            string `gorm:"column:value;type:varchar(255)"`
}

type ProductImage struct {
	ID        int    `gorm:"primary_key"`
	ProductID uint   `gorm:"column:product_id"`
	Image     string `gorm:"column:image;type:varchar(255)"`
}

type City struct {
	CustomModel
	BaseModel
	Name              string `gorm:"column:name"`
	Domain            string `gorm:"column:domain"`
	Address           string `gorm:"column:address"`
	Number            int64  `gorm:"column:number"`
	HowToGetOffice    string `gorm:"column:how_to_get_office"`
	Schedule          string `gorm:"column:schedule"`
	NominativeCase    string `gorm:"column:nominative_case"`
	GenitiveCase      string `gorm:"column:genitive_case"`
	DativeCase        string `gorm:"column:dative_case"`
	AccusativeCase    string `gorm:"column:accusative_case"`
	InstrumentalCase  string `gorm:"column:instrumental_case"`
	PrepositionalCase string `gorm:"column:prepositional_case"`
}

func (Brand) TableName() string {
	return "shop_brand"
}

func (Product) TableName() string {
	return "shop_product"
}

func (ProductImage) TableName() string {
	return "shop_productimage"
}

func (Price) TableName() string {
	return "shop_price"
}

func (Category) TableName() string {
	return "shop_category"
}

func (Characteristic) TableName() string {
	return "shop_characteristic"
}

func (CharacteristicValue) TableName() string {
	return "shop_characteristicvalue"
}

func (City) TableName() string {
	return "account_city"
}

func (CustomUser) TableName() string {
	return "account_customuser"
}

func (cols *Columns) Contains(el string) bool {
	slices.Sort(cols.Cols)

	low := 0
	slice := cols.Cols
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