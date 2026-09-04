import os
import sys
from datetime import datetime, timedelta, date

def seed(force=False):
    from app import create_app
    from app.extensions import db
    from app.models import (
        User, UserRole, Pen, Animal, Sex, Species, Origin, AnimalStatus,
        CIDR, Insemination, HeatNoInsemination, DryOff, Calving, CalvingOffspring, InseminationType, CalvingType,
        TreatmentReproduction, MedicineNoVisit, Vaccination, VisitType,
        Measurement, Quarter, OneTimeEvent, BodyScore, MovementScore, SuggestedSperm, HoofTrimming, MeasurementType, QuarterEnum, HoofStatusEnum,
        MilkRecord, StandardizedMilk, MilkRecordType,
        PenMovement, HerdComposition,
        Sperm, SpermTransaction, StockTransactionType,
        Medicine, MedicineStock,
        LookupItem, ProgramSettings, Staff
    )

    if not force and Animal.query.count() > 0:
        print("Database already contains animal data. Skipping seed.")
        return

    if force:
        print("Force flag set. Recreating all database tables...")
        db.drop_all()
        db.create_all()

    print("Seeding initial demo data...")

    # 1. Create Users
    users = [
        User(username='admin', full_name='مدیر ارشد سیستم', role=UserRole.ADMIN),
        User(username='vet1', full_name='دکتر محمدی (دامپزشک)', role=UserRole.VET),
        User(username='breeder1', full_name='مهندس حسینی (اصلاح نژاد)', role=UserRole.BREEDING_SPECIALIST),
        User(username='operator1', full_name='علی رضایی (اپراتور)', role=UserRole.DATA_ENTRY),
    ]
    for u in users:
        u.set_password('admin123' if u.username == 'admin' else u.username + '123')
        db.session.add(u)
    db.session.commit()
    admin_user = users[0]

    # 2. Lookup Items
    lookups = [
        ('breed', 'افشاری'), ('breed', 'قزل'), ('breed', 'شال'), ('breed', 'رومانی'), ('breed', 'مورسیا (بز)'), ('breed', 'سانن (بز)'),
        ('color', 'سفید'), ('color', 'قهوه‌ای'), ('color', 'مشکی'), ('color', 'حنایی'), ('color', 'ابلق'),
        ('removal_reason', 'فروش پروار'), ('removal_reason', 'کشتار اضطراری'), ('removal_reason', 'پیرسالی'), ('removal_reason', 'حذف فنی/اصلاحی'), ('removal_reason', 'تلفات'),
        ('vaccine_type', 'آبله'), ('vaccine_type', 'شاربن'), ('vaccine_type', 'تب برفکی'), ('vaccine_type', 'انتروتوکسمی'), ('vaccine_type', 'بروسلوز (I2)'),
        ('medicine_category', 'آنتی‌بیوتیک'), ('medicine_category', 'ویتامین و مکمل'), ('medicine_category', 'ضد انگل'), ('medicine_category', 'هورمون'), ('medicine_category', 'مسکن و ضدالتهاب'),
        ('event_type', 'شاخبُری'), ('event_type', 'نصب پلاک جدید'), ('event_type', 'تست سل'), ('event_type', 'خرید و ورود به گله'), ('event_type', 'ارزیابی تیپ')
    ]
    for cat, val in lookups:
        db.session.add(LookupItem(category=cat, value=val))
    db.session.commit()

    # 3. Program Settings
    settings = [
        ProgramSettings(key='min_milk_records', value='3', description='حداقل تعداد رکوردهای شیر برای محاسبه استاندارد'),
        ProgramSettings(key='max_gap_days', value='10', description='حداکثر فاصله مجاز بین دو رکورد شیر (روز)'),
        ProgramSettings(key='default_pregnancy_days', value='150', description='طول دوره بارداری (روز)')
    ]
    for s in settings:
        db.session.add(s)
    db.session.commit()

    # 4. Staff
    staff_members = [
        Staff(full_name='دکتر محمدی', role='دامپزشک مسئول', phone='09121111111'),
        Staff(full_name='مهندس حسینی', role='کارشناس تغذیه و اصلاح نژاد', phone='09122222222'),
        Staff(full_name='حسن کاظمی', role='سرکارگر بهاربندها', phone='09123333333'),
    ]
    for st in staff_members:
        db.session.add(st)
    db.session.commit()

    # 5. Pens
    pens = [
        Pen(name='بهاربند زایمان ۱', code='PEN-DEL-1', capacity=20, pen_type='زایمان', notes='ویژه میش‌ها و بزهای تازه زایمان کرده'),
        Pen(name='بهاربند پرواربندی A', code='PEN-FAT-A', capacity=50, pen_type='پرواربندی', notes='ویژه بره‌ها و بزغاله‌های پرواری'),
        Pen(name='بهاربند نگهداری میش‌ها', code='PEN-EWES-1', capacity=40, pen_type='نگهداری', notes='میش‌ها و بزهای مولد'),
        Pen(name='بهاربند قوچ‌ها و بزها', code='PEN-RAMS-1', capacity=20, pen_type='نگهداری', notes='قوچ‌ها و تکه‌های نر مولد')
    ]
    for p in pens:
        db.session.add(p)
    db.session.commit()

    # 6. Sperms & Sperm Transactions
    sperms = [
        Sperm(name='قوچ افشاری ژن‌دار A1', code='SPM-AF-01', breed='افشاری', internal_reg_no='INT-AF-101', external_reg_no='EXT-AF-550', is_sexed=False),
        Sperm(name='قوچ افشاری ژن‌دار A2', code='SPM-AF-02', breed='افشاری', internal_reg_no='INT-AF-102', external_reg_no='EXT-AF-551', is_sexed=True),
        Sperm(name='قوچ شال ممتاز S1', code='SPM-SH-01', breed='شال', internal_reg_no='INT-SH-201', external_reg_no='EXT-SH-601', is_sexed=False),
        Sperm(name='قوچ رومانی برتر R1', code='SPM-RM-01', breed='رومانی', internal_reg_no='INT-RM-301', external_reg_no='EXT-RM-701', is_sexed=True),
        Sperm(name='بز سانن فرانسوی M1', code='SPM-SN-01', breed='سانن (بز)', internal_reg_no='INT-SN-401', external_reg_no='EXT-SN-801', is_sexed=False),
        Sperm(name='بز مورسیا اسپانیایی MU1', code='SPM-MU-01', breed='مورسیا (بز)', internal_reg_no='INT-MU-501', external_reg_no='EXT-MU-901', is_sexed=False),
        Sperm(name='قوچ قزل اصل Q1', code='SPM-QZ-01', breed='قزل', internal_reg_no='INT-QZ-601', external_reg_no='EXT-QZ-101', is_sexed=False),
        Sperm(name='بز سانن فرانسوی M2', code='SPM-SN-02', breed='سانن (بز)', internal_reg_no='INT-SN-402', external_reg_no='EXT-SN-802', is_sexed=True),
    ]
    for sp in sperms:
        db.session.add(sp)
    db.session.commit()

    today = date.today()

    for sp in sperms:
        tx_in = SpermTransaction(sperm_id=sp.id, transaction_type=StockTransactionType.IN, date=today - timedelta(days=60), form_number='IMP-100', description='ورود اولیه به بانک اسپرم', quantity=50, created_by_user_id=admin_user.id)
        tx_out = SpermTransaction(sperm_id=sp.id, transaction_type=StockTransactionType.OUT, date=today - timedelta(days=20), form_number='USE-105', description='مصرف در عملیات تلقیح', quantity=10, created_by_user_id=admin_user.id)
        db.session.add(tx_in)
        db.session.add(tx_out)
        sp.stock_qty = 40
    db.session.commit()

    # 7. Medicines & Stock
    medicines = [
        Medicine(name='پنی‌سیلین', category='آنتی‌بیوتیک', unit='cc'),
        Medicine(name='اکسی‌تتراسایکلین', category='آنتی‌بیوتیک', unit='cc'),
        Medicine(name='ویتامین AD3E', category='ویتامین و مکمل', unit='cc'),
        Medicine(name='آلبندازول', category='ضد انگل', unit='گرم'),
        Medicine(name='آیورمکتین', category='ضد انگل', unit='cc'),
        Medicine(name='پروستاتگلاندین (PGF2a)', category='هورمون', unit='cc'),
        Medicine(name='واکسن انتروتوکسمی', category='واکسن', unit='دوز'),
        Medicine(name='واکسن آبله', category='واکسن', unit='دوز'),
    ]
    for med in medicines:
        db.session.add(med)
    db.session.commit()

    for med in medicines:
        st_in = MedicineStock(medicine_id=med.id, date=today - timedelta(days=90), transaction_type=StockTransactionType.IN, quantity=500.0, invoice_number='INV-88', supplier='داروخانه مرکزی', created_by_user_id=admin_user.id)
        st_out = MedicineStock(medicine_id=med.id, date=today - timedelta(days=15), transaction_type=StockTransactionType.OUT, quantity=50.0, invoice_number='USE-01', supplier='مصرف درمانگاه', created_by_user_id=admin_user.id)
        db.session.add(st_in)
        db.session.add(st_out)
    db.session.commit()

    # 8. Seed 40 Animals with 3-Generation pedigree lines & half-siblings
    # Founder Generation (Gen 0) - Grandparents
    # G0_M1 (Grandmother 1), G0_F1 (Grandfather 1 / Ram)
    g0_m1 = Animal(plastic_tag='IR-G0-F1', serial_number='SN-0001', birth_date=today - timedelta(days=365*5), sex=Sex.FEMALE, species=Species.SHEEP, breed='افشاری', current_pen_id=pens[2].id, origin=Origin.PURCHASED, status=AnimalStatus.ALIVE)
    g0_f1 = Animal(plastic_tag='IR-G0-M1', serial_number='SN-0002', birth_date=today - timedelta(days=365*5), sex=Sex.MALE, species=Species.SHEEP, breed='افشاری', current_pen_id=pens[3].id, origin=Origin.PURCHASED, status=AnimalStatus.ALIVE)

    # G0_M2 (Grandmother 2), G0_F2 (Grandfather 2 / Goat)
    g0_m2 = Animal(plastic_tag='IR-G0-F2', serial_number='SN-0003', birth_date=today - timedelta(days=365*6), sex=Sex.FEMALE, species=Species.GOAT, breed='سانن (بز)', current_pen_id=pens[2].id, origin=Origin.PURCHASED, status=AnimalStatus.ALIVE)
    g0_f2 = Animal(plastic_tag='IR-G0-M2', serial_number='SN-0004', birth_date=today - timedelta(days=365*6), sex=Sex.MALE, species=Species.GOAT, breed='سانن (بز)', current_pen_id=pens[3].id, origin=Origin.PURCHASED, status=AnimalStatus.ALIVE)

    db.session.add_all([g0_m1, g0_f1, g0_m2, g0_f2])
    db.session.commit()

    # Generation 1 (Parents)
    # Dam 1 (daughter of G0_M1 and G0_F1)
    gen1_dam1 = Animal(plastic_tag='IR-G1-F1', serial_number='SN-0005', birth_date=today - timedelta(days=365*3), sex=Sex.FEMALE, species=Species.SHEEP, breed='افشاری', mother_id=g0_m1.id, father_id=g0_f1.id, current_pen_id=pens[2].id, origin=Origin.BORN_IN_FARM, status=AnimalStatus.ALIVE, parity=2)
    # Dam 2 (daughter of G0_M1 and G0_F1 - full sister to gen1_dam1)
    gen1_dam2 = Animal(plastic_tag='IR-G1-F2', serial_number='SN-0006', birth_date=today - timedelta(days=365*3), sex=Sex.FEMALE, species=Species.SHEEP, breed='افشاری', mother_id=g0_m1.id, father_id=g0_f1.id, current_pen_id=pens[2].id, origin=Origin.BORN_IN_FARM, status=AnimalStatus.ALIVE, parity=2)
    # Sire 1 (son of G0_M1 and another sire) -> shares mother g0_m1 with dam1 and dam2 (half-brother)
    gen1_sire1 = Animal(plastic_tag='IR-G1-M1', serial_number='SN-0007', birth_date=today - timedelta(days=365*3 + 100), sex=Sex.MALE, species=Species.SHEEP, breed='افشاری', mother_id=g0_m1.id, father_sperm_id=sperms[0].id, current_pen_id=pens[3].id, origin=Origin.BORN_IN_FARM, status=AnimalStatus.ALIVE)

    # Goat Dam 1
    gen1_goat1 = Animal(plastic_tag='IR-G1-F3', serial_number='SN-0008', birth_date=today - timedelta(days=365*3), sex=Sex.FEMALE, species=Species.GOAT, breed='سانن (بز)', mother_id=g0_m2.id, father_id=g0_f2.id, current_pen_id=pens[2].id, origin=Origin.BORN_IN_FARM, status=AnimalStatus.ALIVE, parity=2)

    db.session.add_all([gen1_dam1, gen1_dam2, gen1_sire1, gen1_goat1])
    db.session.commit()

    # Generation 2 (Offspring of Gen1)
    # Offspring of half-sibling mating (gen1_dam1 x gen1_sire1) -> yields F = 0.125
    gen2_inbred1 = Animal(plastic_tag='IR-G2-INB1', serial_number='SN-0009', birth_date=today - timedelta(days=365), sex=Sex.FEMALE, species=Species.SHEEP, breed='افشاری', mother_id=gen1_dam1.id, father_id=gen1_sire1.id, current_pen_id=pens[0].id, origin=Origin.BORN_IN_FARM, status=AnimalStatus.ALIVE, parity=1)

    db.session.add(gen2_inbred1)
    db.session.commit()

    # Remaining 31 Animals to reach 40 total
    additional_animals = []
    # 7 Females with full reproduction & milk history
    for i in range(10, 18):
        species_type = Species.SHEEP if i % 2 == 0 else Species.GOAT
        breed_name = 'افشاری' if species_type == Species.SHEEP else 'سانن (بز)'
        a = Animal(
            plastic_tag=f'IR-EW-{i:02d}',
            serial_number=f'SN-{i:04d}',
            birth_date=today - timedelta(days=365*2 + i*20),
            sex=Sex.FEMALE,
            species=species_type,
            breed=breed_name,
            mother_id=g0_m1.id if species_type == Species.SHEEP else g0_m2.id,
            current_pen_id=pens[i % 4].id,
            origin=Origin.BORN_IN_FARM,
            status=AnimalStatus.ALIVE,
            parity=1
        )
        additional_animals.append(a)

    # 10 Males (Rams/Bucks)
    for i in range(18, 28):
        species_type = Species.SHEEP if i % 2 == 0 else Species.GOAT
        breed_name = 'شال' if species_type == Species.SHEEP else 'مورسیا (بز)'
        a = Animal(
            plastic_tag=f'IR-RAM-{i:02d}',
            serial_number=f'SN-{i:04d}',
            birth_date=today - timedelta(days=365*2 + i*15),
            sex=Sex.MALE,
            species=species_type,
            breed=breed_name,
            current_pen_id=pens[3].id,
            origin=Origin.PURCHASED,
            status=AnimalStatus.ALIVE
        )
        additional_animals.append(a)

    # 12 Young Lambs / Kids
    for i in range(28, 40):
        species_type = Species.SHEEP if i % 2 == 0 else Species.GOAT
        breed_name = 'افشاری' if species_type == Species.SHEEP else 'سانن (بز)'
        a = Animal(
            plastic_tag=f'IR-LAMB-{i:02d}',
            serial_number=f'SN-{i:04d}',
            birth_date=today - timedelta(days=60 + i*3),
            sex=Sex.FEMALE if i % 2 == 0 else Sex.MALE,
            species=species_type,
            breed=breed_name,
            mother_id=gen1_dam1.id if species_type == Species.SHEEP else gen1_goat1.id,
            current_pen_id=pens[1].id,
            origin=Origin.BORN_IN_FARM,
            status=AnimalStatus.ALIVE,
            birth_weight=3.8 + (i % 5) * 0.2
        )
        additional_animals.append(a)

    db.session.add_all(additional_animals)
    db.session.commit()

    # 9. Reproduction Records (CIDR -> Insemination -> DryOff -> Calving for 8 females)
    repro_females = [gen1_dam1, gen1_dam2, gen1_goat1, gen2_inbred1] + additional_animals[:4]
    for idx, female in enumerate(repro_females):
        # CIDR
        cidr_rec = CIDR(
            animal_id=female.id,
            insert_date=today - timedelta(days=220),
            remove_date=today - timedelta(days=206),
            cidr_type='EAZI-BREED',
            cidr_number=f'C-{idx+100}',
            notes='سیدرگذاری هورمونی همزمانی فحلی',
            created_by_user_id=admin_user.id
        )
        db.session.add(cidr_rec)

        # Insemination
        insem_rec = Insemination(
            animal_id=female.id,
            date=today - timedelta(days=204),
            time='08:30',
            insemination_type=InseminationType.ARTIFICIAL,
            sperm_id=sperms[idx % len(sperms)].id,
            parity_cycle=female.parity or 1,
            led_to_pregnancy=True,
            notes='تلقیح مصنوعی موفق',
            created_by_user_id=admin_user.id
        )
        db.session.add(insem_rec)

        # Dry Off
        dry_rec = DryOff(
            animal_id=female.id,
            start_date=today - timedelta(days=80),
            end_date=today - timedelta(days=54),
            notes='خشک‌کردن قبل زایش',
            created_by_user_id=admin_user.id
        )
        db.session.add(dry_rec)

        # Calving
        calv_rec = Calving(
            animal_id=female.id,
            date=today - timedelta(days=54),
            calving_type=CalvingType.NORMAL,
            offspring_count=1,
            created_by_user_id=admin_user.id
        )
        db.session.add(calv_rec)
        db.session.commit()

        # Link newborn offspring
        offspring_animal = additional_animals[idx + 12] # lamb/kid
        co = CalvingOffspring(calving_id=calv_rec.id, animal_id=offspring_animal.id)
        db.session.add(co)

    db.session.commit()

    # 10. Milk Records (8 females with regular 6-10 records every 2-3 days; 1 female with sparse/irregular records)
    for idx, female in enumerate(repro_females):
        if idx == 0:
            # Sparse / Irregular female to demonstrate "insufficient data" message
            m_rec = MilkRecord(
                animal_id=female.id,
                date=today - timedelta(days=25),
                record_type=MilkRecordType.OFFICIAL,
                parity_cycle=female.parity or 1,
                milking1_amount=1.2,
                milking2_amount=1.0,
                total_amount=2.2,
                created_by_user_id=admin_user.id
            )
            db.session.add(m_rec)
        else:
            # 8 Regular records
            for r_idx in range(8):
                rec_date = today - timedelta(days=40 - r_idx*3)
                m1 = 1.2 + (r_idx % 3) * 0.1
                m2 = 1.0 + (r_idx % 2) * 0.1
                mr = MilkRecord(
                    animal_id=female.id,
                    date=rec_date,
                    record_type=MilkRecordType.OFFICIAL,
                    parity_cycle=female.parity or 1,
                    milking1_time='06:00',
                    milking1_amount=round(m1, 2),
                    milking2_time='18:00',
                    milking2_amount=round(m2, 2),
                    total_amount=round(m1 + m2, 2),
                    fat_percent=3.5,
                    protein_percent=3.2,
                    created_by_user_id=admin_user.id
                )
                db.session.add(mr)
    db.session.commit()

    # 11. Medical & Measurements (Vaccination, Measurements, Quarters, HoofTrimming, BodyScore, MovementScore)
    all_animals = Animal.query.all()
    for idx, a in enumerate(all_animals[:15]):
        vac = Vaccination(
            animal_id=a.id,
            date=today - timedelta(days=30),
            dose_number='۱',
            vaccine_name='انتروتوکسمی',
            agent_name='دکتر محمدی',
            created_by_user_id=admin_user.id
        )
        meas = Measurement(
            animal_id=a.id,
            date=today - timedelta(days=15),
            measurement_type=MeasurementType.WEIGHT,
            value=45.5 + idx,
            unit='کیلوگرم',
            created_by_user_id=admin_user.id
        )
        bs = BodyScore(
            animal_id=a.id,
            date=today - timedelta(days=15),
            score=3.5,
            created_by_user_id=admin_user.id
        )
        ms = MovementScore(
            animal_id=a.id,
            date=today - timedelta(days=15),
            score=1.0,
            created_by_user_id=admin_user.id
        )
        hoof = HoofTrimming(
            animal_id=a.id,
            date=today - timedelta(days=45),
            front_left_status=HoofStatusEnum.HEALTHY,
            front_right_status=HoofStatusEnum.HEALTHY,
            rear_left_status=HoofStatusEnum.HEALTHY,
            rear_right_status=HoofStatusEnum.HEALTHY,
            created_by_user_id=admin_user.id
        )
        db.session.add_all([vac, meas, bs, ms, hoof])

    for a in repro_females[:5]:
        q = Quarter(
            animal_id=a.id,
            date=today - timedelta(days=10),
            quarter=QuarterEnum.FRONT_LEFT,
            issue_description='بررسی سلامت پستان - وضعیت طبیعی',
            created_by_user_id=admin_user.id
        )
        db.session.add(q)

    # 12. Pen Movement History
    pm = PenMovement(
        animal_id=gen2_inbred1.id,
        date=today - timedelta(days=50),
        from_pen_id=pens[2].id,
        to_pen_id=pens[0].id,
        reason='انتقال به بهاربند زایمان',
        created_by_user_id=admin_user.id
    )
    db.session.add(pm)

    # 13. Herd Composition
    hc = HerdComposition(
        date=today,
        male_count=15,
        female_count=25,
        lamb_count=12,
        pregnant_count=8,
        lactating_count=8,
        dry_count=4,
        total_count=40,
        notes='ترکیب گله بر اساس آخرین سرشماری روزانه',
        created_by_user_id=admin_user.id
    )
    db.session.add(hc)

    db.session.commit()
    print("✅ Demo data successfully seeded: 40 animals, 4 pens, 8 sperms, 8 medicines, reproduction & milk history!")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        force_flag = '--force' in sys.argv
        seed(force=force_flag)
