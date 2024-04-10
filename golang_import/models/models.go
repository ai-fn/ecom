package models

import (
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

type Category struct {
	gorm.Model
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
	gorm.Model
	CategoryID           uint        `gorm:"column:category_id"`
	BrandID              uint        `gorm:"column:brand_id"`
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
	SimilarProducts      []*Product  `gorm:"many2many:product_similar_products"`
	FrequentlyBought     []*Product  `gorm:"many2many:product_frequently_bought_together;"`
}

type Brand struct {
	gorm.Model
	Name  string `gorm:"column:name"`
	Icon  string `gorm:"column:icon;type:varchar(255)"`
	Slug  string `gorm:"column:slug;unique"`
	Order int    `gorm:"column:order"`
}

type Price struct {
	gorm.Model
	ProductID uint     `gorm:"column:product_id"`
	CityID    uint     `gorm:"column:city_id"`
	Price     float64  `gorm:"column:price;type:decimal(10,2)"`
	OldPrice  *float64 `gorm:"column:old_price;type:decimal(10,2)"`
}

type Characteristic struct {
	gorm.Model
	Name       string `gorm:"column:name;unique"`
	CategoryID uint   `gorm:"column:category_id"`
}

type CharacteristicValue struct {
	gorm.Model
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
	gorm.Model
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
