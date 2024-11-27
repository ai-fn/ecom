## v1.1.0 (2024-11-25)

### Feat

- added 'crm_id' field to Product model and make 'crm_id' field nullable in Price model
- updated UserDetailSerializer
- updated User model (email, phone non required, added email index, force deletion)
- updated required unique fields validation (make it nullable and validate on set value)
- added 'crm_id' field into User, Order, Price models
- initialized 'business_ru' crm adapter
- added foreigh key "city" for PickupPoint model


### Fix

- fixed cart migration (typo in getattrs)
- fixed typos in crm_integrations app
- fixed useless creation of a default city when applying migration
- fixed default city setting for PickupPoint model when migrating
- fixed error on empty queryset of categories
- fixed gitlab repo url (with creds)
- make test network non-internal
- include self on category metadata getting
- fix getting category tags
- fix errors with code confirmaiton
