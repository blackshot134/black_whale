from database import SessionLocal, User, MembershipPlan, ServiceStatus
from auth import hash_password
from datetime import datetime

print("🔄 Connecting to database...")
db = SessionLocal()

# 1. ساخت پلن‌ها
plans = [
    {"name": "bronze", "daily_bomber_limit": 50, "daily_search_limit": 20, "monthly_price": 0, "color": "#cd7f32"},
    {"name": "silver", "daily_bomber_limit": 200, "daily_search_limit": 50, "monthly_price": 9.99, "color": "#c0c0c0"},
    {"name": "gold", "daily_bomber_limit": 1000, "daily_search_limit": 200, "monthly_price": 19.99, "color": "#ffd700"},
]

for plan in plans:
    existing = db.query(MembershipPlan).filter(MembershipPlan.name == plan["name"]).first()
    if not existing:
        db.add(MembershipPlan(**plan))
        print(f"✅ Created {plan['name']} plan")

# 2. ساخت ادمین
admin = db.query(User).filter(User.email == "admin@blackwhale.com").first()
if admin:
    db.delete(admin)
    db.commit()
    print("⚠️ Removed old admin")

# ساخت ادمین جدید با هش جدید
admin = User(
    email="admin@blackwhale.com",
    username="admin",
    password_hash=hash_password("admin123"),
    full_name="System Administrator",
    is_verified=True,
    role="admin",
    membership="gold",
    created_at=datetime.now()
)
db.add(admin)
print("✅ Admin created: admin@blackwhale.com / admin123")

# 3. ساخت کاربر تست
test_user = db.query(User).filter(User.email == "test@test.com").first()
if not test_user:
    test_user = User(
        email="test@test.com",
        username="test",
        password_hash=hash_password("test123"),
        full_name="Test User",
        is_verified=True,
        role="user",
        membership="bronze",
        created_at=datetime.now()
    )
    db.add(test_user)
    print("✅ Test user created: test@test.com / test123")

# 4. ساخت سرویس‌ها
services = ["Bomber API", "Sheypoor Scraper", "Divar Scraper", "Search Database", "Email Service"]
for service in services:
    existing = db.query(ServiceStatus).filter(ServiceStatus.service_name == service).first()
    if not existing:
        db.add(ServiceStatus(service_name=service, is_online=True))
        print(f"✅ Created {service}")

db.commit()

# نمایش کاربران
print("\n📊 Users in database:")
for u in db.query(User).all():
    print(f"   {u.email} | {u.username} | verified: {u.is_verified} | role: {u.role}")

db.close()
print("\n✅ Done!")