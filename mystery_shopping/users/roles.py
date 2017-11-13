class UserRole:
    TENANT_PRODUCT_MANAGER_GROUP = 'Tenant Product Managers'
    TENANT_PROJECT_MANAGER_GROUP = 'Tenant Project Managers'
    TENANT_CONSULTANT_GROUP = 'Tenant Consultants'
    CLIENT_PROJECT_MANAGER_GROUP = 'Client Project Managers'
    CLIENT_MANAGER_GROUP = 'Client Managers'
    CLIENT_EMPLOYEE_GROUP = 'Client Employees'
    CLIENT_DETRACTORS_MANAGER_GROUP = 'Detractors Managers'
    COLLECTOR_GROUP = 'collectors'
    SHOPPER_GROUP = 'shoppers'
    TENANT_GROUPS = [TENANT_PRODUCT_MANAGER_GROUP, TENANT_PROJECT_MANAGER_GROUP, TENANT_CONSULTANT_GROUP]
    CLIENT_GROUPS = [CLIENT_PROJECT_MANAGER_GROUP, CLIENT_MANAGER_GROUP, CLIENT_EMPLOYEE_GROUP,
                     CLIENT_DETRACTORS_MANAGER_GROUP]
    SHOPPERS_COLLECTORS = [COLLECTOR_GROUP, SHOPPER_GROUP]

    GROUPS_TO_ROLES = {
        TENANT_PRODUCT_MANAGER_GROUP: 'tenantproductmanager',
        TENANT_PROJECT_MANAGER_GROUP: 'tenantprojectmanager',
        TENANT_CONSULTANT_GROUP: 'tenantconsultant',
        CLIENT_MANAGER_GROUP: 'clientmanager',
        CLIENT_PROJECT_MANAGER_GROUP: 'clientprojectmanager',
        CLIENT_EMPLOYEE_GROUP: 'clientemployee',
        CLIENT_DETRACTORS_MANAGER_GROUP: 'clientdetractorsmanager',
        COLLECTOR_GROUP: 'collector',
        SHOPPER_GROUP: 'shopper'
    }
