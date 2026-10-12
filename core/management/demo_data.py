"""Demo content for local development. Replace through the admin."""

REGIONS = [
    ("north-bali", {"en": "North Bali (Buleleng)", "ru": "Северный Бали (Булеленг)", "tr": "Kuzey Bali (Buleleng)"}),
    ("tabanan", {"en": "Tabanan", "ru": "Табанан", "tr": "Tabanan"}),
    ("bukit", {"en": "Bukit (Badung)", "ru": "Букит (Бадунг)", "tr": "Bukit (Badung)"}),
    ("gianyar", {"en": "Ubud & Gianyar", "ru": "Убуд и Гианьяр", "tr": "Ubud ve Gianyar"}),
    ("sumbawa", {"en": "Sumbawa (NTB)", "ru": "Сумбава (НТБ)", "tr": "Sumbawa (NTB)"}),
]

SITE = {
    "brand": "Bali Islands",
    "legal_name": "PT Bali Islands (demo)",
    "address": "Lovina, Buleleng, Bali, Indonesia",
    "email": "hello@bali-islands.com",
    "whatsapp": "6281200000000",
    "telegram": "baliislands",
    "hero_title": {
        "en": "Exclusive land in Bali, off-market",
        "ru": "Эксклюзивная земля на Бали вне открытого рынка",
        "tr": "Bali'de piyasada olmayan özel araziler",
    },
    "hero_subtitle": {
        "en": "Plots, beachfront land and private islands directly from Indonesian owners — with full legal support and construction.",
        "ru": "Участки, земля у океана и частные острова напрямую от индонезийских собственников — с полным юридическим сопровождением и строительством.",
        "tr": "Endonezyalı sahiplerinden doğrudan arsalar, sahil arazileri ve özel adalar — tam hukuki destek ve inşaat hizmetiyle.",
    },
    "stats": {
        "en": "EN · RU · TR | languages we work in\n100% | documents verified before listing\n1 | partner for the whole deal",
        "ru": "EN · RU · TR | языки, на которых мы работаем\n100% | документов проверяем до публикации\n1 | партнёр на всю сделку",
        "tr": "EN · RU · TR | çalıştığımız diller\n%100 | yayından önce doğrulanan belgeler\n1 | tüm süreç için tek ortak",
    },
}

SERVICES = [
    ("search", {
        "title": {"en": "Land search & due diligence", "ru": "Подбор земли и due diligence", "tr": "Arazi arama ve durum tespiti"},
        "summary": {
            "en": "Certificate check at BPN, zoning (RDTR) verification, access, utilities and the owner's documents — before you pay anything.",
            "ru": "Проверка сертификата в BPN, зонирования (RDTR), подъезда, коммуникаций и документов собственника — до любой оплаты.",
            "tr": "Herhangi bir ödeme yapmadan önce BPN'de tapu kontrolü, imar (RDTR) doğrulaması, yol, altyapı ve mal sahibinin belgeleri.",
        },
    }),
    ("building", {
        "title": {"en": "Ownership structure & PT PMA", "ru": "Структура владения и PT PMA", "tr": "Mülkiyet yapısı ve PT PMA"},
        "summary": {
            "en": "Leasehold, PT PMA with HGB title or Hak Pakai — we choose the right structure for your goals and set up the company.",
            "ru": "Лизхолд, PT PMA с титулом HGB или Hak Pakai — подбираем структуру под ваши цели и регистрируем компанию.",
            "tr": "Kiralama (leasehold), HGB tapulu PT PMA veya Hak Pakai — hedeflerinize uygun yapıyı seçer ve şirketi kurarız.",
        },
    }),
    ("stamp", {
        "title": {"en": "Notary, PPAT & taxes", "ru": "Нотариус, PPAT и налоги", "tr": "Noter, PPAT ve vergiler"},
        "summary": {
            "en": "Preparation of PPJB and AJB, coordination with the notary/PPAT, payment of BPHTB and seller tax, title transfer.",
            "ru": "Подготовка PPJB и AJB, работа с нотариусом/PPAT, оплата BPHTB и налога продавца, переоформление титула.",
            "tr": "PPJB ve AJB hazırlığı, noter/PPAT ile koordinasyon, BPHTB ve satıcı vergisinin ödenmesi, tapu devri.",
        },
    }),
    ("document", {
        "title": {"en": "Permits & licensing", "ru": "Разрешения и лицензии", "tr": "İzinler ve ruhsatlar"},
        "summary": {
            "en": "KKPR, PBG building permit, SLF and business licences through OSS — everything a villa or hotel project needs.",
            "ru": "KKPR, разрешение на строительство PBG, SLF и бизнес-лицензии через OSS — всё, что нужно проекту виллы или отеля.",
            "tr": "KKPR, PBG yapı ruhsatı, SLF ve OSS üzerinden işletme lisansları — bir villa veya otel projesinin ihtiyacı olan her şey.",
        },
    }),
    ("crane", {
        "title": {"en": "Design & construction", "ru": "Проектирование и строительство", "tr": "Tasarım ve inşaat"},
        "summary": {
            "en": "Architects, trusted contractors and on-site supervision with transparent budgets and photo reports.",
            "ru": "Архитекторы, проверенные подрядчики и технадзор на площадке с прозрачной сметой и фотоотчётами.",
            "tr": "Mimarlar, güvenilir müteahhitler ve şeffaf bütçe ile fotoğraflı raporlarla şantiye denetimi.",
        },
    }),
    ("key", {
        "title": {"en": "Handover & management", "ru": "Сдача объекта и управление", "tr": "Teslim ve yönetim"},
        "summary": {
            "en": "Furnishing, rental licences and introduction to management companies so the property works while you are away.",
            "ru": "Меблировка, лицензии на аренду и подбор управляющей компании, чтобы объект работал, пока вас нет на острове.",
            "tr": "Siz yokken mülkün çalışması için mobilya, kiralama lisansları ve yönetim şirketleriyle tanıştırma.",
        },
    }),
]

ABOUT = {
    "title": {
        "en": "Your trusted partner on the ground in Bali",
        "ru": "Ваш надёжный партнёр на Бали",
        "tr": "Bali'de sahadaki güvenilir ortağınız",
    },
    "lead": {
        "en": "I live in Bali and run an Indonesian company that brings foreign investors together with local landowners — and stays with them until the deal is closed and the project is built.",
        "ru": "Я живу на Бали и руковожу индонезийской компанией, которая соединяет иностранных инвесторов с местными собственниками земли и сопровождает их до закрытия сделки и окончания стройки.",
        "tr": "Bali'de yaşıyorum ve yabancı yatırımcıları yerel arazi sahipleriyle buluşturan, anlaşma tamamlanıp proje inşa edilene kadar yanlarında olan bir Endonezya şirketi yönetiyorum.",
    },
    "body": {
        "en": (
            "## How I work\n\n"
            "Most of the land I offer comes from personal relationships with Indonesian families. "
            "These plots and islands are not on public portals, and the owners trust me to find the right buyer.\n\n"
            "My fee is paid by the seller. For you as a buyer, my job is to make the purchase transparent and legally safe.\n\n"
            "## What I take care of\n\n"
            "- Checking the certificate, zoning and the seller's documents\n"
            "- Choosing the ownership structure for a foreign buyer\n"
            "- Working with notaries and PPAT through to title transfer\n"
            "- Permits, architects and construction supervision\n\n"
            "## Edit this text\n\n"
            "This is demo text. Replace it in the admin: Site content → Pages → about."
        ),
        "ru": (
            "## Как я работаю\n\n"
            "Большая часть земли, которую я предлагаю, приходит через личные связи с индонезийскими семьями. "
            "Этих участков и островов нет на открытых площадках, и собственники доверяют мне поиск покупателя.\n\n"
            "Мою комиссию платит продавец. Для вас как покупателя моя задача — сделать покупку прозрачной и юридически безопасной.\n\n"
            "## Чем я занимаюсь\n\n"
            "- Проверка сертификата, зонирования и документов продавца\n"
            "- Выбор структуры владения для иностранного покупателя\n"
            "- Работа с нотариусами и PPAT до переоформления титула\n"
            "- Разрешения, архитекторы и технадзор на стройке\n\n"
            "## Отредактируйте этот текст\n\n"
            "Это демо-текст. Замените его в админке: Site content → Pages → about."
        ),
        "tr": (
            "## Nasıl çalışıyorum\n\n"
            "Sunduğum arazilerin çoğu Endonezyalı ailelerle kişisel ilişkilerden gelir. "
            "Bu arsalar ve adalar açık portallarda yer almaz ve sahipleri doğru alıcıyı bulmam için bana güvenir.\n\n"
            "Ücretimi satıcı öder. Alıcı olarak sizin için görevim, satın almayı şeffaf ve hukuken güvenli kılmaktır.\n\n"
            "## Neleri üstleniyorum\n\n"
            "- Tapunun, imarın ve satıcının belgelerinin kontrolü\n"
            "- Yabancı alıcı için mülkiyet yapısının seçimi\n"
            "- Tapu devrine kadar noter ve PPAT ile çalışma\n"
            "- İzinler, mimarlar ve inşaat denetimi\n\n"
            "## Bu metni düzenleyin\n\n"
            "Bu bir demo metindir. Yönetim panelinden değiştirin: Site content → Pages → about."
        ),
    },
}

HOW_TO_BUY = {
    "title": {
        "en": "How a foreigner can buy land in Indonesia",
        "ru": "Как иностранцу купить землю в Индонезии",
        "tr": "Bir yabancı Endonezya'da nasıl arazi satın alabilir",
    },
    "lead": {
        "en": "Freehold (Hak Milik) is reserved for Indonesian citizens, but foreign buyers have several legal and well-established ways to own and use land.",
        "ru": "Право полной собственности (Hak Milik) есть только у граждан Индонезии, но у иностранцев есть несколько законных и отработанных способов владеть землёй и пользоваться ею.",
        "tr": "Tam mülkiyet (Hak Milik) Endonezya vatandaşlarına aittir, ancak yabancı alıcıların araziye sahip olmak ve kullanmak için birkaç yasal ve yerleşik yolu vardır.",
    },
    "body": {
        "en": (
            "## 1. Leasehold (Hak Sewa)\n\n"
            "A long-term lease registered with a notary, typically 25–30 years with an extension option. "
            "The simplest route for a private villa or a first investment.\n\n"
            "## 2. PT PMA with HGB title\n\n"
            "A foreign-owned Indonesian company can hold land under Hak Guna Bangunan (right to build): "
            "up to 30 years, extendable by 20 and renewable by 30. Suitable for rental villas, hotels and development.\n\n"
            "## 3. Hak Pakai (right to use)\n\n"
            "Available to foreigners with a residence permit for a residential property, and to PT PMA companies. "
            "Terms are similar to HGB.\n\n"
            "## Islands and coastal land\n\n"
            "Small islands have a special regime: foreign investment needs a permit from the Ministry of Marine Affairs and Fisheries, "
            "part of the island remains public, and the project must follow the coastal zoning plan. We prepare this process together with licensed consultants.\n\n"
            "## The deal step by step\n\n"
            "- Site visit, drone footage and preliminary check of the certificate\n"
            "- Due diligence: BPN certificate check, zoning (RDTR / KKPR), access and boundaries\n"
            "- Agreement on price and structure, deposit under a preliminary agreement (PPJB)\n"
            "- Signing the deed (AJB) or lease agreement with a notary / PPAT\n"
            "- Payment of taxes and registration of the title in your name or your company's name\n\n"
            "## Taxes and costs (typical)\n\n"
            "- Buyer: BPHTB acquisition tax — 5% of the transaction value (minus a small allowance)\n"
            "- Seller: final income tax — 2.5%\n"
            "- Notary / PPAT: usually about 1%\n\n"
            "**This page is general information, not legal advice.** Each deal is reviewed individually with a notary."
        ),
        "ru": (
            "## 1. Лизхолд (Hak Sewa)\n\n"
            "Долгосрочная аренда, оформленная у нотариуса, обычно на 25–30 лет с правом продления. "
            "Самый простой вариант для частной виллы или первой инвестиции.\n\n"
            "## 2. PT PMA с титулом HGB\n\n"
            "Индонезийская компания с иностранным капиталом может владеть землёй на праве Hak Guna Bangunan (право застройки): "
            "до 30 лет, с продлением на 20 и обновлением на 30. Подходит для арендных вилл, отелей и девелопмента.\n\n"
            "## 3. Hak Pakai (право пользования)\n\n"
            "Доступно иностранцам с видом на жительство для жилой недвижимости и компаниям PT PMA. "
            "Сроки сопоставимы с HGB.\n\n"
            "## Острова и прибрежная земля\n\n"
            "Для малых островов действует особый режим: иностранным инвестициям нужно разрешение Министерства морских дел и рыболовства, "
            "часть острова остаётся общественной, а проект должен соответствовать плану прибрежного зонирования. Мы готовим этот процесс вместе с лицензированными консультантами.\n\n"
            "## Сделка по шагам\n\n"
            "- Осмотр участка, съёмка с дрона и предварительная проверка сертификата\n"
            "- Due diligence: проверка сертификата в BPN, зонирование (RDTR / KKPR), подъезд и границы\n"
            "- Согласование цены и структуры, задаток по предварительному договору (PPJB)\n"
            "- Подписание акта (AJB) или договора аренды у нотариуса / PPAT\n"
            "- Оплата налогов и регистрация титула на вас или вашу компанию\n\n"
            "## Налоги и расходы (обычно)\n\n"
            "- Покупатель: налог BPHTB — 5% от суммы сделки (за вычетом небольшого необлагаемого минимума)\n"
            "- Продавец: финальный налог на доход — 2,5%\n"
            "- Нотариус / PPAT: обычно около 1%\n\n"
            "**Эта страница — общая информация, а не юридическая консультация.** Каждая сделка проверяется индивидуально с нотариусом."
        ),
        "tr": (
            "## 1. Uzun süreli kira (Hak Sewa)\n\n"
            "Noter huzurunda kayıt altına alınan, genellikle 25–30 yıllık ve uzatma seçenekli uzun süreli kira. "
            "Özel bir villa veya ilk yatırım için en basit yol.\n\n"
            "## 2. HGB tapulu PT PMA\n\n"
            "Yabancı sermayeli bir Endonezya şirketi araziye Hak Guna Bangunan (inşa hakkı) ile sahip olabilir: "
            "30 yıla kadar, 20 yıl uzatılabilir ve 30 yıl yenilenebilir. Kiralık villalar, oteller ve geliştirme projeleri için uygundur.\n\n"
            "## 3. Hak Pakai (kullanım hakkı)\n\n"
            "Oturma izni olan yabancılar için konut amaçlı ve PT PMA şirketleri için kullanılabilir. "
            "Süreler HGB'ye benzerdir.\n\n"
            "## Adalar ve kıyı arazileri\n\n"
            "Küçük adalar için özel bir rejim geçerlidir: yabancı yatırım Denizcilik ve Balıkçılık Bakanlığı'ndan izin gerektirir, "
            "adanın bir kısmı kamuya açık kalır ve proje kıyı imar planına uymalıdır. Bu süreci lisanslı danışmanlarla birlikte hazırlıyoruz.\n\n"
            "## Adım adım satın alma\n\n"
            "- Arazi ziyareti, drone çekimi ve tapunun ön kontrolü\n"
            "- Durum tespiti: BPN tapu kontrolü, imar (RDTR / KKPR), yol ve sınırlar\n"
            "- Fiyat ve yapı üzerinde anlaşma, ön sözleşme (PPJB) ile kapora\n"
            "- Noter / PPAT huzurunda tapu senedinin (AJB) veya kira sözleşmesinin imzalanması\n"
            "- Vergilerin ödenmesi ve tapunun sizin veya şirketinizin adına tescili\n\n"
            "## Vergiler ve masraflar (tipik)\n\n"
            "- Alıcı: BPHTB edinim vergisi — işlem bedelinin %5'i (küçük bir muafiyet düşülerek)\n"
            "- Satıcı: nihai gelir vergisi — %2,5\n"
            "- Noter / PPAT: genellikle yaklaşık %1\n\n"
            "**Bu sayfa genel bilgi niteliğindedir, hukuki tavsiye değildir.** Her işlem noterle ayrı ayrı incelenir."
        ),
    },
}

LEGAL_PAGES = {
    "privacy": {
        "title": {"en": "Privacy policy", "ru": "Политика конфиденциальности", "tr": "Gizlilik politikası"},
        "body": {
            "en": "We collect only the contact details you send through the forms (name, phone, email, Telegram, message) and use them solely to answer your request.\n\nWe do not sell or share your data with third parties, except notaries and consultants involved in your deal with your consent.\n\nTo delete your data, write to us by email.\n\n**Demo text — replace with your own policy.**",
            "ru": "Мы собираем только контактные данные, которые вы отправляете через формы (имя, телефон, email, Telegram, сообщение), и используем их исключительно для ответа на ваш запрос.\n\nМы не продаём и не передаём ваши данные третьим лицам, кроме нотариусов и консультантов, участвующих в вашей сделке, с вашего согласия.\n\nЧтобы удалить свои данные, напишите нам на email.\n\n**Демо-текст — замените на свою политику.**",
            "tr": "Yalnızca formlar aracılığıyla gönderdiğiniz iletişim bilgilerini (ad, telefon, e-posta, Telegram, mesaj) toplarız ve bunları yalnızca talebinize yanıt vermek için kullanırız.\n\nVerilerinizi, onayınızla işleminizde yer alan noterler ve danışmanlar dışında üçüncü taraflara satmaz veya paylaşmayız.\n\nVerilerinizi silmek için bize e-posta gönderin.\n\n**Demo metin — kendi politikanızla değiştirin.**",
        },
    },
    "terms": {
        "title": {"en": "Terms of use", "ru": "Условия использования", "tr": "Kullanım koşulları"},
        "body": {
            "en": "Information on this website is provided for general guidance and does not constitute an offer or legal advice. Prices and availability may change without notice.\n\n**Demo text — replace with your own terms.**",
            "ru": "Информация на сайте носит ознакомительный характер и не является офертой или юридической консультацией. Цены и наличие объектов могут меняться без уведомления.\n\n**Демо-текст — замените на свои условия.**",
            "tr": "Bu web sitesindeki bilgiler genel bilgilendirme amaçlıdır ve bir teklif veya hukuki tavsiye niteliği taşımaz. Fiyatlar ve müsaitlik önceden haber verilmeksizin değişebilir.\n\n**Demo metin — kendi koşullarınızla değiştirin.**",
        },
    },
}

# palette: (sky top, sky bottom, sea/land, foreground)
PROPERTIES = [
    {
        "region": "north-bali",
        "kind": "land",
        "status": "published",
        "featured": True,
        "location": "Tukad Mungga, Lovina",
        "lat": "-8.172400", "lng": "115.019800",
        "area": 1850, "price": 296000,
        "title_type": "shm", "zoning": "tourism",
        "features": {"road_access": True, "electricity": True, "water": True, "ocean_view": True},
        "beach": 1.8, "airport": 85,
        "palette": [(42, 76, 92), (214, 168, 120), (54, 96, 74), (24, 44, 34)],
        "title": {
            "en": "Ocean-view hillside plot in Lovina",
            "ru": "Участок на холме с видом на океан в Ловине",
            "tr": "Lovina'da okyanus manzaralı yamaç arsası",
        },
        "summary": {
            "en": "A gently sloping plot above Lovina with an open view of the Bali Sea — ideal for 3–4 villas.",
            "ru": "Участок с плавным уклоном над Ловиной и открытым видом на Балийское море — идеален для 3–4 вилл.",
            "tr": "Lovina'nın üzerinde, Bali Denizi'ne açık manzaralı hafif eğimli bir arsa — 3–4 villa için ideal.",
        },
        "description": {
            "en": "The plot sits on the first line of hills above Lovina, ten minutes from the beach and the town centre. Sunsets over the sea are visible from the entire upper part of the land.\n\nThe owner is a local family; the certificate (SHM) has been checked and the land is in the tourism zone, which allows villas and small hospitality projects.",
            "ru": "Участок расположен на первой линии холмов над Ловиной, в десяти минутах от пляжа и центра. Закаты над морем видны со всей верхней части участка.\n\nСобственник — местная семья; сертификат (SHM) проверен, земля находится в туристической зоне, что позволяет строить виллы и небольшие гостиничные проекты.",
            "tr": "Arsa, Lovina'nın üzerindeki ilk tepe sırasında, sahile ve şehir merkezine on dakika mesafededir. Deniz üzerindeki gün batımları arazinin tüm üst kısmından görülebilir.\n\nMal sahibi yerel bir ailedir; tapu (SHM) kontrol edilmiştir ve arazi villa ve küçük konaklama projelerine izin veren turizm bölgesindedir.",
        },
        "highlights": {
            "en": "Unobstructed sea view\nTourism zoning (pink)\nPaved road to the plot\nElectricity and well on site",
            "ru": "Открытый вид на море\nТуристическая зона (розовая)\nАсфальтированная дорога до участка\nЭлектричество и скважина на участке",
            "tr": "Engelsiz deniz manzarası\nTurizm imarı (pembe)\nArsaya asfalt yol\nArazide elektrik ve kuyu",
        },
    },
    {
        "region": "north-bali",
        "kind": "beachfront",
        "status": "published",
        "featured": True,
        "location": "Pemuteran",
        "lat": "-8.141900", "lng": "114.656200",
        "area": 4200, "price": 630000,
        "title_type": "shm", "zoning": "tourism",
        "features": {"road_access": True, "electricity": True, "water": True, "ocean_view": True, "beachfront": True},
        "beach": 0, "airport": 120,
        "palette": [(70, 120, 150), (230, 200, 150), (40, 110, 130), (194, 170, 120)],
        "title": {
            "en": "Beachfront land in Pemuteran",
            "ru": "Земля на первой линии в Пемутеране",
            "tr": "Pemuteran'da sahil arazisi",
        },
        "summary": {
            "en": "42 are directly on a calm black-sand beach next to coral reefs — a rare plot for a boutique resort.",
            "ru": "42 сотки прямо на спокойном пляже с чёрным песком рядом с коралловыми рифами — редкий участок под бутик-отель.",
            "tr": "Mercan resiflerinin yanında sakin, siyah kumlu bir plajın hemen üzerinde 42 ar — butik bir tatil köyü için nadir bir arsa.",
        },
        "description": {
            "en": "Pemuteran is the diving capital of North Bali, close to Menjangan Island and the West Bali National Park. The plot has 40 metres of beach frontage and a flat surface ready for construction.",
            "ru": "Пемутеран — дайверская столица Северного Бали, рядом с островом Менджанган и национальным парком Западный Бали. У участка 40 метров береговой линии и ровная поверхность, готовая к строительству.",
            "tr": "Pemuteran, Menjangan Adası ve Batı Bali Milli Parkı'na yakın, Kuzey Bali'nin dalış başkentidir. Arsanın 40 metre sahil cephesi ve inşaata hazır düz bir yüzeyi vardır.",
        },
        "highlights": {
            "en": "40 m beach frontage\nFlat, ready to build\nNext to coral reefs\nQuiet, upscale area",
            "ru": "40 м береговой линии\nРовный, готов к стройке\nРядом коралловые рифы\nТихий, престижный район",
            "tr": "40 m sahil cephesi\nDüz, inşaata hazır\nMercan resiflerinin yanında\nSakin, seçkin bölge",
        },
    },
    {
        "region": "tabanan",
        "kind": "land",
        "status": "published",
        "featured": True,
        "location": "Kedungu",
        "lat": "-8.611200", "lng": "115.087400",
        "area": 1200, "price": 216000,
        "title_type": "shm", "zoning": "residential",
        "features": {"road_access": True, "electricity": True},
        "beach": 1.2, "airport": 35,
        "palette": [(120, 160, 170), (236, 214, 160), (92, 140, 70), (60, 100, 50)],
        "title": {
            "en": "Rice-field view plot near Kedungu",
            "ru": "Участок с видом на рисовые поля у Кедунгу",
            "tr": "Kedungu yakınında pirinç tarlası manzaralı arsa",
        },
        "summary": {
            "en": "12 are surrounded by rice terraces, minutes from the Kedungu surf break — a growing villa area.",
            "ru": "12 соток в окружении рисовых террас, в паре минут от сёрф-спота Кедунгу — быстро растущий район вилл.",
            "tr": "Kedungu sörf noktasına dakikalar mesafede, pirinç terasları ile çevrili 12 ar — gelişen bir villa bölgesi.",
        },
        "description": {
            "en": "Kedungu is becoming the next Canggu, but quieter and greener. The plot is in the residential (yellow) zone with road access and electricity at the boundary.",
            "ru": "Кедунгу становится новым Чангу, только тише и зеленее. Участок в жилой (жёлтой) зоне, с подъездом и электричеством на границе.",
            "tr": "Kedungu yeni Canggu olmaya aday, ancak daha sakin ve daha yeşil. Arsa, yol erişimi ve sınırda elektrikle konut (sarı) bölgesindedir.",
        },
        "highlights": {
            "en": "Residential zoning (yellow)\nProtected rice-field view\n35 minutes to the airport",
            "ru": "Жилая зона (жёлтая)\nЗащищённый вид на рисовые поля\n35 минут до аэропорта",
            "tr": "Konut imarı (sarı)\nKorunan pirinç tarlası manzarası\nHavalimanına 35 dakika",
        },
    },
    {
        "region": "bukit",
        "kind": "land",
        "status": "published",
        "featured": False,
        "location": "Uluwatu",
        "lat": "-8.815800", "lng": "115.114900",
        "area": 2500, "price": None, "on_request": True,
        "title_type": "leasehold", "lease_years": 35, "zoning": "tourism",
        "features": {"road_access": True, "electricity": True, "water": True, "ocean_view": True},
        "beach": 0.6, "airport": 16,
        "palette": [(60, 110, 160), (240, 190, 130), (30, 90, 130), (170, 150, 110)],
        "title": {
            "en": "Clifftop land in Uluwatu",
            "ru": "Земля на скале в Улувату",
            "tr": "Uluwatu'da uçurum üstü arazi",
        },
        "summary": {
            "en": "25 are on the cliff edge with a 180° Indian Ocean view. Long-term lease, price on request.",
            "ru": "25 соток на краю скалы с видом на Индийский океан на 180°. Долгосрочная аренда, цена по запросу.",
            "tr": "Hint Okyanusu'na 180° manzaralı, uçurum kenarında 25 ar. Uzun süreli kira, fiyat talep üzerine.",
        },
        "description": {
            "en": "One of the last clifftop plots in this part of Uluwatu. The lease is offered for 35 years with an extension option, registered with a notary.",
            "ru": "Один из последних участков на скале в этой части Улувату. Аренда предлагается на 35 лет с правом продления, с регистрацией у нотариуса.",
            "tr": "Uluwatu'nun bu bölgesindeki son uçurum üstü arsalardan biri. Kira, uzatma seçeneğiyle 35 yıllığına noter kaydıyla sunulmaktadır.",
        },
        "highlights": {
            "en": "180° ocean view\n35-year lease + extension\n15 minutes to world-class surf",
            "ru": "Вид на океан 180°\nАренда 35 лет + продление\n15 минут до сёрф-спотов мирового уровня",
            "tr": "180° okyanus manzarası\n35 yıl kira + uzatma\nDünya standartlarında sörfe 15 dakika",
        },
    },
    {
        "region": "sumbawa",
        "kind": "island",
        "status": "unlisted",
        "featured": False,
        "location": "Saleh Bay",
        "lat": "-8.420000", "lng": "117.640000",
        "area": 80000, "price": 1900000,
        "title_type": "hak_pakai", "zoning": "tourism",
        "features": {"ocean_view": True, "beachfront": True},
        "beach": 0, "airport": 60,
        "palette": [(40, 120, 160), (220, 230, 220), (20, 130, 150), (60, 120, 70)],
        "title": {
            "en": "Private island in Saleh Bay, Sumbawa",
            "ru": "Частный остров в заливе Салех, Сумбава",
            "tr": "Saleh Körfezi'nde özel ada, Sumbawa",
        },
        "summary": {
            "en": "8 hectares with white-sand beaches and a lagoon — a rare opportunity for an eco-resort. Shown by private link only.",
            "ru": "8 гектаров с белыми пляжами и лагуной — редкая возможность для эко-курорта. Показывается только по ссылке.",
            "tr": "Beyaz kumlu plajları ve lagünüyle 8 hektar — bir eko tatil köyü için nadir bir fırsat. Yalnızca özel bağlantıyla gösterilir.",
        },
        "description": {
            "en": "A small island in the calm waters of Saleh Bay, about an hour by boat from the Sumbawa coast. Ideal for a low-density eco-resort or a private retreat.",
            "ru": "Небольшой остров в спокойных водах залива Салех, примерно в часе на лодке от побережья Сумбавы. Идеален для эко-курорта с низкой плотностью застройки или частной резиденции.",
            "tr": "Saleh Körfezi'nin sakin sularında, Sumbawa kıyısından tekneyle yaklaşık bir saat uzaklıkta küçük bir ada. Düşük yoğunluklu bir eko tatil köyü veya özel bir inziva yeri için ideal.",
        },
        "legal_notes": {
            "en": "Foreign investment on small islands requires a permit from the Ministry of Marine Affairs and Fisheries and is structured through a PT PMA. We prepare the full process with licensed consultants.",
            "ru": "Иностранные инвестиции на малых островах требуют разрешения Министерства морских дел и рыболовства и оформляются через PT PMA. Мы готовим весь процесс вместе с лицензированными консультантами.",
            "tr": "Küçük adalarda yabancı yatırım, Denizcilik ve Balıkçılık Bakanlığı'ndan izin gerektirir ve PT PMA aracılığıyla yapılandırılır. Tüm süreci lisanslı danışmanlarla birlikte hazırlıyoruz.",
        },
        "highlights": {
            "en": "8 ha, several beaches\nSheltered lagoon\nCoral reefs around the island",
            "ru": "8 га, несколько пляжей\nЗащищённая лагуна\nКоралловые рифы вокруг острова",
            "tr": "8 ha, birkaç plaj\nKorunaklı lagün\nAdanın etrafında mercan resifleri",
        },
    },
]
