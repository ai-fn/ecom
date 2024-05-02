module utils

go 1.22.1

require (
	github.com/google/uuid v1.6.0
	github.com/jinzhu/gorm v1.9.16
	github.com/nfnt/resize v0.0.0-20180221191011-83c6a9932646
	github.com/xuri/excelize/v2 v2.8.1
	models v0.0.0-00010101000000-000000000000
)

require (
	github.com/jinzhu/inflection v1.0.0 // indirect
	github.com/lib/pq v1.1.1 // indirect
	github.com/mohae/deepcopy v0.0.0-20170929034955-c48cc78d4826 // indirect
	github.com/richardlehane/mscfb v1.0.4 // indirect
	github.com/richardlehane/msoleps v1.0.3 // indirect
	github.com/xuri/efp v0.0.0-20231025114914-d1ff6096ae53 // indirect
	github.com/xuri/nfp v0.0.0-20230919160717-d98342af3f05 // indirect
	golang.org/x/crypto v0.19.0 // indirect
	golang.org/x/net v0.21.0 // indirect
	golang.org/x/text v0.14.0 // indirect
)

replace models => ../models
