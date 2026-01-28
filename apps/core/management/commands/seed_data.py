"""
Lao Job Website - Seed Data Command
Populates database with initial provinces, categories, and other reference data.
"""
from django.core.management.base import BaseCommand
from django.db import transaction


# Provinces (18 ແຂວງ)
PROVINCES = [
    {"id": 1, "name": "ນະຄອນຫຼວງວຽງຈັນ", "name_en": "Vientiane Capital", "slug": "vientiane-capital", "sort_order": 1},
    {"id": 2, "name": "ຜົ້ງສາລີ", "name_en": "Phongsali", "slug": "phongsali", "sort_order": 2},
    {"id": 3, "name": "ຫຼວງນ້ຳທາ", "name_en": "Luang Namtha", "slug": "luang-namtha", "sort_order": 3},
    {"id": 4, "name": "ອຸດົມໄຊ", "name_en": "Oudomxai", "slug": "oudomxai", "sort_order": 4},
    {"id": 5, "name": "ບໍ່ແກ້ວ", "name_en": "Bokeo", "slug": "bokeo", "sort_order": 5},
    {"id": 6, "name": "ຫຼວງພະບາງ", "name_en": "Luang Prabang", "slug": "luang-prabang", "sort_order": 6},
    {"id": 7, "name": "ຫົວພັນ", "name_en": "Houaphanh", "slug": "houaphanh", "sort_order": 7},
    {"id": 8, "name": "ໄຊຍະບູລີ", "name_en": "Xaignabouli", "slug": "xaignabouli", "sort_order": 8},
    {"id": 9, "name": "ຊຽງຂວາງ", "name_en": "Xiengkhouang", "slug": "xiengkhouang", "sort_order": 9},
    {"id": 10, "name": "ວຽງຈັນ", "name_en": "Vientiane Province", "slug": "vientiane-province", "sort_order": 10},
    {"id": 11, "name": "ບໍລິຄຳໄຊ", "name_en": "Bolikhamxai", "slug": "bolikhamxai", "sort_order": 11},
    {"id": 12, "name": "ຄຳມ່ວນ", "name_en": "Khammouane", "slug": "khammouane", "sort_order": 12},
    {"id": 13, "name": "ສະຫວັນນະເຂດ", "name_en": "Savannakhet", "slug": "savannakhet", "sort_order": 13},
    {"id": 14, "name": "ສາລະວັນ", "name_en": "Salavan", "slug": "salavan", "sort_order": 14},
    {"id": 15, "name": "ເຊກອງ", "name_en": "Sekong", "slug": "sekong", "sort_order": 15},
    {"id": 16, "name": "ຈຳປາສັກ", "name_en": "Champasak", "slug": "champasak", "sort_order": 16},
    {"id": 17, "name": "ອັດຕະປື", "name_en": "Attapeu", "slug": "attapeu", "sort_order": 17},
    {"id": 18, "name": "ໄຊສົມບູນ", "name_en": "Xaisomboun", "slug": "xaisomboun", "sort_order": 18},
]

# Categories (ໝວດໝູ່ວຽກ)
CATEGORIES = [
    {"id": 1, "name": "ໄອທີ/ຄອມພິວເຕີ", "name_en": "IT/Computer", "slug": "it-computer", "icon": "laptop", "sort_order": 1},
    {"id": 2, "name": "ບັນຊີ/ການເງິນ", "name_en": "Accounting/Finance", "slug": "accounting-finance", "icon": "chart-bar", "sort_order": 2},
    {"id": 3, "name": "ການຕະຫຼາດ/ຂາຍ", "name_en": "Marketing/Sales", "slug": "marketing-sales", "icon": "trending-up", "sort_order": 3},
    {"id": 4, "name": "ບໍລິຫານ/ຈັດການ", "name_en": "Admin/Management", "slug": "admin-management", "icon": "briefcase", "sort_order": 4},
    {"id": 5, "name": "ວິສະວະກຳ", "name_en": "Engineering", "slug": "engineering", "icon": "cog", "sort_order": 5},
    {"id": 6, "name": "ໂຮງງານ/ຜະລິດ", "name_en": "Manufacturing", "slug": "manufacturing", "icon": "factory", "sort_order": 6},
    {"id": 7, "name": "ຂົນສົ່ງ/ໂລຈິສຕິກ", "name_en": "Logistics/Transport", "slug": "logistics-transport", "icon": "truck", "sort_order": 7},
    {"id": 8, "name": "ການກໍ່ສ້າງ", "name_en": "Construction", "slug": "construction", "icon": "hard-hat", "sort_order": 8},
    {"id": 9, "name": "ການສຶກສາ/ຝຶກອົບຮົມ", "name_en": "Education/Training", "slug": "education-training", "icon": "graduation-cap", "sort_order": 9},
    {"id": 10, "name": "ສາທາລະນະສຸກ", "name_en": "Healthcare", "slug": "healthcare", "icon": "hospital", "sort_order": 10},
    {"id": 11, "name": "ຮ້ານອາຫານ/ໂຮງແຮມ", "name_en": "Hospitality", "slug": "hospitality", "icon": "utensils", "sort_order": 11},
    {"id": 12, "name": "ຄ້າປີກ/ຮ້ານຄ້າ", "name_en": "Retail", "slug": "retail", "icon": "shopping-cart", "sort_order": 12},
    {"id": 13, "name": "ທະນາຄານ/ປະກັນໄພ", "name_en": "Banking/Insurance", "slug": "banking-insurance", "icon": "landmark", "sort_order": 13},
    {"id": 14, "name": "ກົດໝາຍ", "name_en": "Legal", "slug": "legal", "icon": "scale", "sort_order": 14},
    {"id": 15, "name": "ສື່ສານມວນຊົນ/ການອອກແບບ", "name_en": "Media/Design", "slug": "media-design", "icon": "palette", "sort_order": 15},
    {"id": 16, "name": "ອື່ນໆ", "name_en": "Others", "slug": "others", "icon": "tag", "sort_order": 99},
]

# Report Reasons
REPORT_REASONS = [
    {"id": 1, "name": "ວຽກປອມ/ຫຼອກລວງ", "sort_order": 1},
    {"id": 2, "name": "ເນື້ອໃນບໍ່ເໝາະສົມ", "sort_order": 2},
    {"id": 3, "name": "ຂໍ້ມູນບໍ່ຖືກຕ້ອງ", "sort_order": 3},
    {"id": 4, "name": "ໂພສຊ້ຳ", "sort_order": 4},
    {"id": 5, "name": "ສະແປມ/ໂຄສະນາ", "sort_order": 5},
    {"id": 6, "name": "ອື່ນໆ", "sort_order": 99},
]

# Subscription Plans
SUBSCRIPTION_PLANS = [
    {
        "id": 1,
        "name": "ແພັກເກດ 1 ປີ",
        "price": 2000000,
        "duration_days": 365,
        "description": "ໂພສວຽກໄດ້ບໍ່ຈຳກັດ ຕະຫຼອດ 1 ປີ",
        "features": [
            "ໂພສວຽກບໍ່ຈຳກັດ",
            "ແຕ່ລະໂພສມີອາຍຸ 15 ມື້",
            "ເບິ່ງສະຖິຕິໂພສ",
            "ຮັບໃບສະໝັກຜ່ານລະບົບ",
            "ແຈ້ງເຕືອນໃບສະໝັກໃໝ່",
        ],
        "is_active": True,
        "sort_order": 1,
    },
]

# Quick Filters
QUICK_FILTERS = [
    {"id": 1, "name": "ໃກ້ຂ້ອຍ", "icon": "map-pin", "filter_params": {"near_me": True}, "sort_order": 1},
    {"id": 2, "name": "ເງິນເດືອນສູງ", "icon": "dollar-sign", "filter_params": {"salary_min": 10000000, "order_by": "-salary_max"}, "sort_order": 2},
    {"id": 3, "name": "ໂພສມື້ນີ້", "icon": "clock", "filter_params": {"posted_today": True}, "sort_order": 3},
    {"id": 4, "name": "ບໍ່ຕ້ອງມີປະສົບການ", "icon": "graduation-cap", "filter_params": {"no_experience": True}, "sort_order": 4},
    {"id": 5, "name": "ເຮັດວຽກຈາກບ້ານ", "icon": "home", "filter_params": {"remote": True}, "sort_order": 5},
    {"id": 6, "name": "Part-time", "icon": "clock", "filter_params": {"job_type": "part_time"}, "sort_order": 6},
    {"id": 7, "name": "ມີປະກັນສັງຄົມ", "icon": "shield", "filter_params": {"has_insurance": True}, "sort_order": 7},
    {"id": 8, "name": "ໃກ້ໝົດອາຍຸ", "icon": "alert-circle", "filter_params": {"expiring_soon": True, "order_by": "expires_at"}, "sort_order": 8},
]

# Job Templates
JOB_TEMPLATES = [
    {
        "id": 1,
        "name": "ພະນັກງານຂາຍ",
        "icon": "shopping-cart",
        "template_type": "system",
        "title_template": "ພະນັກງານຂາຍ",
        "category_id": 3,
        "job_type": "full_time",
        "description_template": """ພວກເຮົາກຳລັງຊອກຫາພະນັກງານຂາຍທີ່ມີຄວາມກະຕືລືລົ້ນເພື່ອເຂົ້າຮ່ວມທີມຂອງພວກເຮົາ.

ໜ້າທີ່ຮັບຜິດຊອບ:
• ຕ້ອນຮັບລູກຄ້າແລະໃຫ້ຄຳແນະນຳສິນຄ້າ
• ດຳເນີນການຂາຍແລະປິດການຂາຍ
• ຈັດວາງສິນຄ້າໃຫ້ສວຍງາມ
• ຮັກສາຄວາມສະອາດຂອງພື້ນທີ່ຂາຍ
• ລາຍງານຍອດຂາຍປະຈຳວັນ""",
        "requirements_template": """ຄຸນສົມບັດ:
• ອາຍຸ 18-35 ປີ
• ມີບຸກຄະລິກະພາບດີ ຍິ້ມແຍ້ມ ມ່ວນຊື່ນ
• ສາມາດເຮັດວຽກເປັນກະ/ວັນເສົາ-ອາທິດໄດ້
• ບໍ່ຈຳເປັນຕ້ອງມີປະສົບການ (ມີການຝຶກອົບຮົມ)
• ສາມາດເຮັດວຽກເປັນທີມໄດ້""",
        "benefits_template": """ສະຫວັດດີການ:
• ເງິນເດືອນພື້ນຖານ + ຄອມມິດຊັ່ນ
• ປະກັນສັງຄົມ
• ວັນພັກປະຈຳປີ
• ໂບນັດປະຈຳປີ
• ໂອກາດກ້າວໜ້າໃນອາຊີບ""",
        "sort_order": 1,
    },
    {
        "id": 2,
        "name": "ພະນັກງານບັນຊີ",
        "icon": "calculator",
        "template_type": "system",
        "title_template": "ພະນັກງານບັນຊີ",
        "category_id": 2,
        "job_type": "full_time",
        "description_template": """ພວກເຮົາກຳລັງຊອກຫາພະນັກງານບັນຊີເພື່ອດູແລບັນຊີຂອງບໍລິສັດ.

ໜ້າທີ່ຮັບຜິດຊອບ:
• ບັນທຶກບັນຊີລາຍຮັບ-ລາຍຈ່າຍປະຈຳວັນ
• ກະກຽມເອກະສານພາສີ
• ຈັດທຳລາຍງານການເງິນປະຈຳເດືອນ
• ຕິດຕາມລູກໜີ້-ເຈົ້າໜີ້
• ປະສານງານກັບຜູ້ກວດສອບບັນຊີ""",
        "requirements_template": """ຄຸນສົມບັດ:
• ຈົບປະລິນຍາຕີ ຫຼື ທຽບເທົ່າ ສາຂາບັນຊີ/ການເງິນ
• ມີປະສົບການ 1-3 ປີ (ພິຈາລະນາເປັນພິເສດ)
• ໃຊ້ Microsoft Excel ໄດ້ດີ
• ມີຄວາມລະອຽດ ຮອບຄອບ
• ໃຊ້ໂປຣແກຣມບັນຊີໄດ້ (ຖ້າມີ)""",
        "benefits_template": """ສະຫວັດດີການ:
• ປະກັນສັງຄົມ
• ປະກັນສຸຂະພາບ
• ໂບນັດປະຈຳປີ
• ພັກຜ່ອນປະຈຳປີ 15 ມື້
• ການຝຶກອົບຮົມພັດທະນາສີມືແຮງງານ""",
        "sort_order": 2,
    },
    {
        "id": 3,
        "name": "ຄົນຂັບລົດ",
        "icon": "truck",
        "template_type": "system",
        "title_template": "ຄົນຂັບລົດ",
        "category_id": 7,
        "job_type": "full_time",
        "description_template": """ຕ້ອງການຄົນຂັບລົດເພື່ອຂົນສົ່ງສິນຄ້າ/ຮັບສົ່ງພະນັກງານ.

ໜ້າທີ່ຮັບຜິດຊອບ:
• ຂັບລົດຕາມຈຸດໝາຍທີ່ກຳນົດ
• ດູແລຮັກສາລົດໃຫ້ພ້ອມໃຊ້ງານ
• ຂົນສົ່ງສິນຄ້າຢ່າງປອດໄພ
• ບັນທຶກລະຍະທາງແລະນ້ຳມັນ
• ປະຕິບັດຕາມກົດຈາລະຈອນ""",
        "requirements_template": """ຄຸນສົມບັດ:
• ມີໃບຂັບຂີ່ປະເພດ B ຂຶ້ນໄປ
• ມີປະສົບການຂັບລົດຢ່າງໜ້ອຍ 2 ປີ
• ຮູ້ເສັ້ນທາງໃນເມືອງດີ
• ບໍ່ມີປະຫວັດອຸບັດຕິເຫດຮ້າຍແຮງ
• ສຸຂະພາບແຂງແຮງ ສາຍຕາປົກກະຕິ""",
        "benefits_template": """ສະຫວັດດີການ:
• ເງິນເດືອນປະຈຳ
• ຄ່ານ້ຳມັນ (ຖ້າໃຊ້ລົດຕົນເອງ)
• ປະກັນສັງຄົມ
• ໂບນັດປະຈຳປີ""",
        "sort_order": 3,
    },
    {
        "id": 4,
        "name": "ພະນັກງານຮ້ານອາຫານ",
        "icon": "utensils",
        "template_type": "system",
        "title_template": "ພະນັກງານຮ້ານອາຫານ",
        "category_id": 11,
        "job_type": "full_time",
        "description_template": """ຕ້ອງການພະນັກງານຮ້ານອາຫານ ທັງ Front ແລະ Back.

ໜ້າທີ່ຮັບຜິດຊອບ:
• ຕ້ອນຮັບລູກຄ້າ / ບໍລິການ
• ຮັບອໍເດີ້ແລະເສີບອາຫານ
• ຊ່ວຍວຽກຄົວ (ຖ້າຕ້ອງການ)
• ຮັກສາຄວາມສະອາດຂອງຮ້ານ
• ຈັດໂຕະ ເກັບໂຕະ""",
        "requirements_template": """ຄຸນສົມບັດ:
• ອາຍຸ 18-35 ປີ
• ຂະຫຍັນ ອົດທົນ ມັກບໍລິການ
• ສາມາດເຮັດວຽກເປັນກະໄດ້
• ບໍ່ຕ້ອງມີປະສົບການ (ມີການຝຶກ)
• ສຸຂະພາບດີ""",
        "benefits_template": """ສະຫວັດດີການ:
• ເງິນເດືອນ + ຄ່າບໍລິການ
• ອາຫານຟຣີ 2 ຄາບ
• ທີ່ພັກ (ຖ້າມີ)
• ປະກັນສັງຄົມ""",
        "sort_order": 4,
    },
    {
        "id": 5,
        "name": "ພະນັກງານໂຮງງານ",
        "icon": "factory",
        "template_type": "system",
        "title_template": "ພະນັກງານໂຮງງານ",
        "category_id": 6,
        "job_type": "full_time",
        "description_template": """ຮັບສະໝັກພະນັກງານໂຮງງານ ຫຼາຍຕຳແໜ່ງ.

ໜ້າທີ່ຮັບຜິດຊອບ:
• ປະຈຳສາຍການຜະລິດ
• ກວດສອບຄຸນນະພາບສິນຄ້າ
• ຈັດເກັບສິນຄ້າ
• ປະຕິບັດຕາມກົດລະບຽບຄວາມປອດໄພ
• ລາຍງານບັນຫາໃຫ້ຫົວໜ້າ""",
        "requirements_template": """ຄຸນສົມບັດ:
• ອາຍຸ 18-45 ປີ
• ສຸຂະພາບແຂງແຮງ
• ສາມາດເຮັດວຽກເປັນກະໄດ້
• ບໍ່ຕ້ອງມີປະສົບການ
• ຂະຫຍັນ ອົດທົນ""",
        "benefits_template": """ສະຫວັດດີການ:
• ເງິນເດືອນ + OT
• ປະກັນສັງຄົມ
• ລົດຮັບສົ່ງ (ບາງສາຍ)
• ອາຫານກາງວັນ
• ໂບນັດປະຈຳປີ""",
        "sort_order": 5,
    },
    {
        "id": 6,
        "name": "IT/ໂປຣແກຣມເມີ",
        "icon": "laptop",
        "template_type": "system",
        "title_template": "ໂປຣແກຣມເມີ / Developer",
        "category_id": 1,
        "job_type": "full_time",
        "description_template": """ກຳລັງຊອກຫານັກພັດທະນາຊອບແວ ເພື່ອເຂົ້າຮ່ວມທີມ IT.

ໜ້າທີ່ຮັບຜິດຊອບ:
• ພັດທະນາແລະດູແລຮັກສາລະບົບ
• ຂຽນ code ຕາມ requirement
• ທົດສອບແລະແກ້ bug
• ເຮັດວຽກຮ່ວມກັບທີມ
• ຕິດຕາມເຕັກໂນໂລຢີໃໝ່ໆ""",
        "requirements_template": """ຄຸນສົມບັດ:
• ຈົບປະລິນຍາຕີ ສາຂາ IT ຫຼື ທີ່ກ່ຽວຂ້ອງ
• ມີປະສົບການ 1-3 ປີ
• ຊຳນານ: [ໃສ່ພາສາ/Framework]
• ຮູ້ Git, Database
• ມີຄວາມຮັບຜິດຊອບ ເຮັດວຽກເປັນທີມໄດ້""",
        "benefits_template": """ສະຫວັດດີການ:
• ເງິນເດືອນແຂ່ງຂັນໄດ້
• ປະກັນສັງຄົມ + ປະກັນສຸຂະພາບ
• WFH ບາງມື້ (ຖ້າມີ)
• ຄ່າ Internet/ໂທລະສັບ
• ງົບຝຶກອົບຮົມປະຈຳປີ""",
        "sort_order": 6,
    },
]


class Command(BaseCommand):
    help = 'Seed initial data for Lao Job Website'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from apps.jobs.models import Province, Category, QuickFilter, JobTemplate
        from apps.billing.models import SubscriptionPlan
        from apps.reports.models import ReportReason

        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Province.objects.all().delete()
            Category.objects.all().delete()
            ReportReason.objects.all().delete()
            SubscriptionPlan.objects.all().delete()
            QuickFilter.objects.all().delete()
            JobTemplate.objects.all().delete()

        # Seed Provinces
        self.stdout.write('Seeding provinces...')
        for p in PROVINCES:
            Province.objects.update_or_create(
                id=p['id'],
                defaults={
                    'name': p['name'],
                    'name_en': p['name_en'],
                    'slug': p['slug'],
                    'sort_order': p['sort_order'],
                    'is_active': True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  Created {len(PROVINCES)} provinces'))

        # Seed Categories
        self.stdout.write('Seeding categories...')
        for c in CATEGORIES:
            Category.objects.update_or_create(
                id=c['id'],
                defaults={
                    'name': c['name'],
                    'name_en': c['name_en'],
                    'slug': c['slug'],
                    'icon': c['icon'],
                    'sort_order': c['sort_order'],
                    'is_active': True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  Created {len(CATEGORIES)} categories'))

        # Seed Report Reasons
        self.stdout.write('Seeding report reasons...')
        for r in REPORT_REASONS:
            ReportReason.objects.update_or_create(
                id=r['id'],
                defaults={
                    'name': r['name'],
                    'sort_order': r['sort_order'],
                    'is_active': True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  Created {len(REPORT_REASONS)} report reasons'))

        # Seed Subscription Plans
        self.stdout.write('Seeding subscription plans...')
        for p in SUBSCRIPTION_PLANS:
            SubscriptionPlan.objects.update_or_create(
                id=p['id'],
                defaults={
                    'name': p['name'],
                    'price': p['price'],
                    'duration_days': p['duration_days'],
                    'description': p['description'],
                    'features': p['features'],
                    'is_active': p['is_active'],
                    'sort_order': p['sort_order'],
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  Created {len(SUBSCRIPTION_PLANS)} subscription plans'))

        # Seed Quick Filters
        self.stdout.write('Seeding quick filters...')
        for f in QUICK_FILTERS:
            QuickFilter.objects.update_or_create(
                id=f['id'],
                defaults={
                    'name': f['name'],
                    'icon': f['icon'],
                    'filter_params': f['filter_params'],
                    'sort_order': f['sort_order'],
                    'is_active': True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  Created {len(QUICK_FILTERS)} quick filters'))

        # Seed Job Templates
        self.stdout.write('Seeding job templates...')
        for t in JOB_TEMPLATES:
            category = Category.objects.filter(id=t.get('category_id')).first()
            JobTemplate.objects.update_or_create(
                id=t['id'],
                defaults={
                    'name': t['name'],
                    'icon': t['icon'],
                    'template_type': t['template_type'],
                    'title_template': t['title_template'],
                    'category': category,
                    'job_type': t.get('job_type', ''),
                    'description_template': t['description_template'],
                    'requirements_template': t['requirements_template'],
                    'benefits_template': t['benefits_template'],
                    'sort_order': t['sort_order'],
                    'is_active': True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  Created {len(JOB_TEMPLATES)} job templates'))

        self.stdout.write(self.style.SUCCESS('\nData seeding completed!'))
