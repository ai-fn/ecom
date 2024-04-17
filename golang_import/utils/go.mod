module utils

go 1.22.1

require (
	github.com/google/uuid v1.6.0
	github.com/jinzhu/gorm v1.9.16
	github.com/nfnt/resize v0.0.0-20180221191011-83c6a9932646
	models v0.0.0-00010101000000-000000000000
)

require (
	github.com/jinzhu/inflection v1.0.0 // indirect
	github.com/lib/pq v1.1.1 // indirect
)

replace models => ../models
