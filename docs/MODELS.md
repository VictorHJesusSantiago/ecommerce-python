# Models Documentation

## Users App
- **User**: Custom user model with email authentication
- **Address**: User shipping/billing addresses
- **PaymentMethod**: Saved payment methods
- **VendorProfile**: Vendor shop profiles
- **UserActivity**: User activity tracking
- **UserSession**: Active user sessions

## Products App
- **Category**: Product categories (MPTT)
- **Brand**: Product brands
- **Product**: Main product model
- **ProductVariant**: Product variants (size, color, etc.)
- **ProductImage**: Product images
- **ProductAttribute**: Custom attributes
- **ProductCollection**: Product groupings

## Orders App
- **Order**: Customer orders
- **OrderItem**: Individual order items
- **Shipment**: Shipping information
- **ReturnRequest**: Return/refund requests

## Cart App
- **Cart**: Shopping cart
- **CartItem**: Items in cart
- **SavedItem**: Wishlist items

## Payments App
- **PaymentGateway**: Payment provider configs
- **Transaction**: Payment transactions
- **Refund**: Refund records

## Inventory App
- **Warehouse**: Storage locations
- **StockItem**: Product stock levels
- **StockMovement**: Stock change history
- **Supplier**: Product suppliers

## Marketing App
- **Coupon**: Discount coupons
- **Promotion**: Sales promotions
- **Banner**: Site banners
- **Newsletter**: Email subscribers
- **EmailCampaign**: Marketing emails

## Reviews App
- **Review**: Product reviews
- **ReviewVote**: Helpful votes
- **ReviewReport**: Review reports

## CMS App
- **Page**: Static pages
- **Menu**: Navigation menus
- **FAQ**: Frequently asked questions
- **Testimonial**: Customer testimonials
- **ContactMessage**: Contact form submissions
