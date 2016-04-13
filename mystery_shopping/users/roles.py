class UserRole:
    TENANT_PRODUCT_MANAGER = 'tenantproductmanager'
    TENANT_PROJECT_MANAGER = 'tenantprojectmanager'
    TENANT_CONSULTANT = 'tenantconsultant'
    SHOPPER = 'shopper'
    COLLECTOR = 'collector'
    CLIENT_PROJECT_MANAGER = 'clientprojectmanager'
    CLIENT_MANAGER = 'clientmanager'
    CLIENT_EMPLOYEE = 'clientemployee'

    TENANT_USERS = (TENANT_PRODUCT_MANAGER, TENANT_PROJECT_MANAGER, TENANT_CONSULTANT)
    CLIENT_USERS = (CLIENT_PROJECT_MANAGER, CLIENT_MANAGER, CLIENT_EMPLOYEE)