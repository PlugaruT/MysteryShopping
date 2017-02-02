class UserRole:
    TENANT_PRODUCT_MANAGER = 'tenantproductmanager'
    TENANT_PROJECT_MANAGER = 'tenantprojectmanager'
    TENANT_CONSULTANT = 'tenantconsultant'
    SHOPPER = 'shopper'
    COLLECTOR = 'collector'
    CLIENT_PROJECT_MANAGER = 'clientprojectmanager'
    CLIENT_MANAGER = 'clientmanager'
    CLIENT_EMPLOYEE = 'clientemployee'

    TENANT_PRODUCT_MANAGER_GROUP = 'Tenant Product Managers'
    TENANT_PROJECT_MANAGER_GROUP = 'Tenant Project Managers'
    TENANT_CONSULTANT_GROUP = 'Tenant Consultants'
    CLIENT_PROJECT_MANAGER_GROUP = 'Client Project Managers'
    CLIENT_MANAGER_GROUP = 'Client Managers'
    CLIENT_EMPLOYEE_GROUP = 'Client Employees'
    COLLECTOR_GROUP = 'collectors'
    SHOPPER_GROUP = 'shoppers'
    TENANT_GROUPS = [TENANT_PRODUCT_MANAGER_GROUP, TENANT_PROJECT_MANAGER_GROUP, TENANT_CONSULTANT_GROUP]
    CLIENT_GROUPS = [CLIENT_PROJECT_MANAGER_GROUP, CLIENT_MANAGER_GROUP, CLIENT_EMPLOYEE_GROUP]
    SHOPPERS_COLLECTORS = [COLLECTOR_GROUP, SHOPPER_GROUP]

    GROUPS_TO_ROLES = {
        TENANT_PRODUCT_MANAGER_GROUP: 'tenantproductmanager',
        TENANT_PROJECT_MANAGER_GROUP: 'tenantprojectmanager',
        TENANT_CONSULTANT_GROUP: 'tenantconsultant',
        CLIENT_MANAGER_GROUP: 'clientmanager',
        CLIENT_PROJECT_MANAGER_GROUP: 'clientprojectmanager',
        CLIENT_EMPLOYEE_GROUP: 'clientemployee',
        COLLECTOR_GROUP: 'collector',
        SHOPPER_GROUP: 'shopper'
    }

    TENANT_USERS = (TENANT_PRODUCT_MANAGER, TENANT_PROJECT_MANAGER, TENANT_CONSULTANT)
    CLIENT_USERS = (CLIENT_PROJECT_MANAGER, CLIENT_MANAGER, CLIENT_EMPLOYEE)
