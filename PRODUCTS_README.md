# Products API

This Django application implements a comprehensive products management system with **4 different price types** for different user roles, ensuring that each user type sees only the appropriate pricing information.

## 🏷️ **Price Structure**

### **1. End User Price (AI-Generated Retail Market Price)**
- **Target Users**: B2C Visitors, General Public
- **Example**: 150 L.E for 1 KG frozen chicken (retail market price)
- **Access**: Public, visible to all users

### **2. Retail Price for B2C (Business to Customer)**
- **Target Users**: B2C Visitors, Small Business Owners
- **Example**: 2000 L.E for 20 KG package
- **Access**: B2C Visitors, B2C Business Users

### **3. Retail Price for Corporates/Purchasing Managers**
- **Target Users**: Corporate Users, Purchasing Managers
- **Example**: 1850 L.E for 20 KG package
- **Access**: Corporate Users, Storage Clients

### **4. Retail Price for HoReCa**
- **Target Users**: Hotels, Restaurants, Cafes
- **Example**: 1900 L.E for 20 KG package
- **Access**: HoReCa Users

### **5. Wholesale Price for Purchasing Managers**
- **Target Users**: Suppliers, Corporate Users (Bulk Orders)
- **Example**: 1800 L.E for 20 KG package (Minimum 5 packages)
- **Access**: Suppliers, Supplier Merchants, Corporate Users (with quantity requirements)

## 🔐 **Role-Based Price Access**

| User Role | End User Price | B2C Price | Corporate Price | HoReCa Price | Wholesale Price |
|-----------|----------------|-----------|-----------------|---------------|-----------------|
| **B2C Visitor** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Corporate** | ✅ | ❌ | ✅ | ❌ | ✅ (with min quantity) |
| **HoReCa** | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Supplier** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Supplier & Merchant** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Storage Client** | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |

## 🗄️ **Database Schema**

### **Product Model**
```python
class Product(models.Model):
    # Basic Information
    name_en = models.CharField(max_length=200)  # English name
    name_ar = models.CharField(max_length=200)  # Arabic name
    image = models.ImageField(upload_to='products/')
    description_en = models.TextField()  # English description
    description_ar = models.TextField()  # Arabic description
    
    # Classification
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)
    unit = models.CharField(max_length=50, default="KG")  # KG, Package, etc.
    unit_size = models.DecimalField(default=1.0)  # Size of unit
    
    # Pricing (4 different price types)
    end_user_price = models.DecimalField()  # Retail market price
    retail_price_b2c = models.DecimalField()  # B2C wholesale price
    retail_price_corporate = models.DecimalField()  # Corporate price
    retail_price_horeca = models.DecimalField()  # HoReCa price
    wholesale_price = models.DecimalField()  # Bulk order price
    wholesale_min_quantity = models.PositiveIntegerField(default=5)
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    # Supplier
    supplier = models.ForeignKey(User, limit_choices_to={'role__in': ['supplier', 'supplier_merchant']})
    
    # Timestamps & Soft Delete
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
```

## 🌐 **API Endpoints**

### **Product Management**
- `GET /products/` - List all products (with role-based pricing)
- `GET /products/{id}/` - Get product details (with role-based pricing)
- `POST /products/` - Create new product (suppliers only)
- `PUT /products/{id}/` - Update product (suppliers and admins only)
- `DELETE /products/{id}/` - Soft delete product (suppliers and admins only)

### **Product Search & Filtering**
- `GET /products/search/` - Advanced search with filters
- `GET /products/category/{category_name}/` - Products by category
- `GET /products/supplier/{supplier_id}/` - Products by supplier

### **Product Categories**
- `GET /categories/` - List all categories
- `GET /categories/{id}/` - Get category details

### **Product Images**
- `GET /images/` - List product images
- `POST /images/` - Add product image (suppliers and admins only)
- `PUT /images/{id}/` - Update image (suppliers and admins only)
- `DELETE /images/{id}/` - Delete image (suppliers and admins only)

## 📝 **API Usage Examples**

### **1. List Products (Role-Based Pricing)**
```bash
# Get products with pricing based on user role
GET /products/
Authorization: Bearer <jwt_token>

# Response will show appropriate price for user role
{
  "id": 1,
  "name_en": "Frozen Chicken",
  "name_ar": "دجاج مجمد",
  "price_for_user": 1850.00,  # Based on user role
  "price_display": "1850.00 L.E per 20.0 KG"
}
```

### **2. Create Product (Suppliers Only)**
```bash
POST /products/
Authorization: Bearer <supplier_jwt_token>
Content-Type: application/json

{
  "name_en": "Fresh Beef",
  "name_ar": "لحم بقري طازج",
  "description_en": "Premium beef cuts",
  "description_ar": "قطع لحم بقري مميزة",
  "category": "Red Meat",
  "subcategory": "Beef",
  "unit": "KG",
  "unit_size": 1.0,
  "end_user_price": 250.00,
  "retail_price_b2c": 3000.00,
  "retail_price_corporate": 2800.00,
  "retail_price_horeca": 2850.00,
  "wholesale_price": 2700.00,
  "wholesale_min_quantity": 3,
  "stock_quantity": 500
}
```

### **3. Search Products with Filters**
```bash
GET /products/search/?query=chicken&category=Poultry&min_price=100&max_price=2000
Authorization: Bearer <jwt_token>

# Price filtering is automatically role-based
```

### **4. Get Products by Category**
```bash
GET /products/category/Poultry/
Authorization: Bearer <jwt_token>
```

## 🔍 **Search & Filtering Options**

### **Text Search**
- Search in product names (English & Arabic)
- Search in descriptions (English & Arabic)

### **Category Filtering**
- Filter by main category
- Filter by subcategory

### **Price Filtering (Role-Based)**
- `min_price`: Minimum price filter (based on user role)
- `max_price`: Maximum price filter (based on user role)

### **Supplier Filtering**
- Filter by supplier username

### **Availability Filtering**
- `available_only`: Show only available products

### **Pagination**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

## 🛡️ **Security & Permissions**

### **Product Creation**
- **Only Suppliers** can create products
- Validation ensures price logic (wholesale < retail)

### **Product Modification**
- **Suppliers** can only modify their own products
- **Admins** can modify any product

### **Product Deletion**
- Soft delete (products are marked as deleted, not removed)
- **Suppliers** can only delete their own products
- **Admins** can delete any product

### **Price Visibility**
- Each user sees only the prices appropriate for their role
- Admins see all prices for management purposes

## 🧪 **Testing & Sample Data**

### **Create Sample Products**
```bash
# Create sample products for testing
python manage.py create_sample_products --supplier-username supplier_user

# Clear existing sample products
python manage.py create_sample_products --clear
```

### **Sample Product Data**
The management command creates 5 sample products:
1. **Frozen Chicken** - 150 L.E/KG (end user) to 1800 L.E/20KG (wholesale)
2. **Fresh Beef** - 250 L.E/KG (end user) to 2700 L.E/12KG (wholesale)
3. **Fresh Fish** - 180 L.E/KG (end user) to 1750 L.E/10KG (wholesale)
4. **Vegetables Package** - 80 L.E/5KG (end user) to 100 L.E/5KG (wholesale)
5. **Dairy Package** - 120 L.E/3KG (end user) to 155 L.E/3KG (wholesale)

## 📊 **Admin Interface**

### **Product Management**
- View all products with pricing information
- Filter by category, supplier, availability
- Bulk actions (make available/unavailable, restore deleted)

### **Category Management**
- Create and manage product categories
- Hierarchical category structure

### **Image Management**
- Upload and manage product images
- Set primary images and ordering

## 🚀 **Getting Started**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Run Migrations**
```bash
python manage.py makemigrations products
python manage.py migrate
```

### **3. Create Sample Data**
```bash
# First create a supplier user
python manage.py create_user supplier_user password123 supplier --business-type "Food Supplier"

# Then create sample products
python manage.py create_sample_products --supplier-username supplier_user
```

### **4. Test the API**
```bash
# Start the server
python manage.py runserver

# Test endpoints
curl http://127.0.0.1:8000/products/
curl http://127.0.0.1:8000/products/search/?query=chicken
```

## 🔧 **Configuration**

### **Settings**
- Add `'products'` to `INSTALLED_APPS`
- Configure media settings for image uploads
- Set up CORS for frontend integration

### **URLs**
- Include products URLs in main URL configuration
- Products are accessible at `/products/`

## 📈 **Future Enhancements**

- **AI Price Generation**: Automatically generate end user prices
- **Dynamic Pricing**: Real-time price updates based on market conditions
- **Bulk Operations**: Import/export products via CSV/Excel
- **Price History**: Track price changes over time
- **Inventory Management**: Advanced stock tracking and alerts
- **Supplier Portal**: Dedicated interface for suppliers
- **Analytics Dashboard**: Sales and pricing analytics

## 🐛 **Troubleshooting**

### **Common Issues**
1. **Permission Denied**: Ensure user has appropriate role
2. **Price Not Visible**: Check user authentication and role
3. **Image Upload Fails**: Verify media directory permissions
4. **Search Not Working**: Check query parameters and filters

### **Debug Mode**
- Enable Django debug mode for detailed error messages
- Check Django logs for API request/response details
- Use Django admin to verify data integrity

---

The Products API provides a robust, secure, and role-based product management system that ensures each user type sees only the pricing information appropriate for their business needs. The system automatically handles price filtering, validation, and access control based on user roles.
