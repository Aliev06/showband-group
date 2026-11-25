"""Xidmət səhifələrinin (/toy/, /korporativ/, /ad-gunu/) RU / EN tərcüməsi. pages.py-dəki PAGES / SEO / FAQ ilə eyni quruluş."""

UI = {
 'ru': {'pk': 'Пакеты и цены', 'add': 'Можно добавить', 'pdf': 'Все пакеты — PDF', 'faq': 'Частые вопросы', 'other': 'Другие услуги',
        'more': 'Подробнее →', 'chip': 'Showband Group · Баку', 'home': 'Главная', 'video': 'видео',
        'links': {'toy': 'Свадьба и помолвка', 'korporativ': 'Корпоратив', 'ad-gunu': 'День рождения и party'},
        'extra': {'toy': ['Звук, свет и сцена', 'Декор и дизайн площадки', 'Фото, видео и Love Story'],
                  'korporativ': ['Декор и брендинг', 'Фото и видео'], 'ad-gunu': ['Декор и тематический дизайн', 'Фото и видео']}},
 'en': {'pk': 'Packages and prices', 'add': 'Can be added', 'pdf': 'All packages — PDF', 'faq': 'FAQ', 'other': 'Other services',
        'more': 'Details →', 'chip': 'Showband Group · Baku', 'home': 'Home', 'video': 'video',
        'links': {'toy': 'Weddings & engagements', 'korporativ': 'Corporate', 'ad-gunu': 'Birthdays & parties'},
        'extra': {'toy': ['Sound, light and stage', 'Decor and venue design', 'Photo, video and Love Story'],
                  'korporativ': ['Decor and branding', 'Photo and video'], 'ad-gunu': ['Decor and themed design', 'Photo and video']}},
}

PAGES = {'ru': {}, 'en': {}}
PAGES['ru']['toy'] = dict(
 title='Организация свадьбы в Баку — живая музыка, шоу и DJ',
 desc='Организация свадьбы и помолвки в Баку: живой бэнд, шоумен, DJ, первый танец, сюрпризы и финальное шоу. Звук, свет, декор, фото и видео — всё от одной команды.',
 h1='Организация <em>свадьбы</em> в Баку — живая музыка и шоу',
 lead='Каждым моментом вашей свадьбы — от выхода жениха и невесты до первого танца и финального шоу — управляет одна команда: живой бэнд, шоумен, DJ, звук, свет и декор.',
 inc=['DJ, Live Band и шоумен', 'Сценарий и сюрпризы', 'Звук, свет и декор', 'Фото и видео'],
 about=[('Живой бэнд и шоумен', 'Гости не сидят в телефонах: живое исполнение, интерактивное шоу и энергичный ведущий держат зал на ногах весь вечер.'),
        ('Первый танец и сюрпризы', 'Выход пары, первый танец, торт и финальное шоу — всё заранее прописано в сценарии и происходит вовремя.'),
        ('Звук, свет и декор', 'Профессиональный звук, освещение, лазерные шоу и оформление зала под концепцию — от одной команды.')],
 venues='Выступали в Altun Saray, Neapol Saray и других банкетных залах Баку.',
 wa='Здравствуйте! Хочу узнать о свадьбе.')
PAGES['en']['toy'] = dict(
 title='Wedding planning in Baku — live music, show and DJ',
 desc='Wedding and engagement planning in Baku: live band, showman, DJ, first dance, surprises and a final show. Sound, light, decor, photo and video — all from one team.',
 h1='Weddings in <em>Baku</em> — live music and show',
 lead='Every moment of your wedding — from the couple’s entrance to the first dance and the final show — is run by one team: live band, showman, DJ, sound, light and decor.',
 inc=['DJ, Live Band and Showman', 'Script and surprises', 'Sound, light and decor', 'Photo and video'],
 about=[('Live band and showman', 'Guests don’t sit on their phones: live music, an interactive show and an energetic host keep the hall dancing all night.'),
        ('First dance and surprises', 'The couple’s entrance, first dance, cake moment and final show — all scripted in advance and on time.'),
        ('Sound, light and decor', 'Professional sound, lighting, laser shows and venue decor to match your concept — from one team.')],
 venues='We have performed at Altun Saray, Neapol Saray and other wedding halls in Baku.',
 wa='Hello! I would like to know more about a wedding.')

PAGES['ru']['korporativ'] = dict(
 title='Организация корпоративов в Баку — ведущий и шоу',
 desc='Организация корпоративов в Баку: вечера компании, презентации, новогодние программы — ведущий, шоу, Live Band или DJ, звук и свет, сцена и брендированный декор.',
 h1='Организация <em>корпоративов</em> в Баку',
 lead='Корпоративные вечера, презентации, новогодние и праздничные программы: ведущий, шоу, живая музыка, сцена и брендированный декор — всё от одной команды.',
 inc=['Ведущий и шоу-программа', 'Live Band или DJ', 'Звук, свет и сцена', 'Брендированный декор', 'Фото и видео'],
 about=[('Ведущий и программа', 'Переход от официальной части к развлечениям, награждения, интерактивные игры — сценарий готовим под вашу компанию.'),
        ('Live Band или DJ', 'В зависимости от формата — живое исполнение, DJ или оба; национальный и современный репертуар.'),
        ('Сцена и бренд', 'Сцена, свет, экраны и декор в цветах вашего бренда — мероприятие выглядит в стиле компании.')],
 venues='Организуем корпоративные вечера, презентации и праздничные мероприятия.',
 wa='Здравствуйте! Хочу узнать о корпоративе.')
PAGES['en']['korporativ'] = dict(
 title='Corporate event planning in Baku — host and show',
 desc='Corporate events in Baku: company parties, presentations, New Year programmes — host, show, Live Band or DJ, sound and light, stage and branded decor.',
 h1='Corporate <em>events</em> in Baku',
 lead='Company parties, presentations, New Year and holiday programmes: host, show, live music, stage and branded decor — all from one team.',
 inc=['Host and show programme', 'Live Band or DJ', 'Sound, light and stage', 'Branded decor', 'Photo and video'],
 about=[('Host and programme', 'A smooth move from the official part to entertainment, awards, interactive games — the script is built for your company.'),
        ('Live Band or DJ', 'Depending on the format — live music, a DJ or both; national and modern repertoire.'),
        ('Stage and brand', 'Stage, lighting, screens and decor in your brand colours — the event looks like your company.')],
 venues='We organise corporate parties, presentations and holiday events.',
 wa='Hello! I would like to know more about a corporate event.')

PAGES['ru']['ad-gunu'] = dict(
 title='Организация дня рождения в Баку — DJ, шоумен и шоу',
 desc='Организация дня рождения и вечеринок в Баку: DJ, шоумен, игры, лазерное и световое шоу, тематический декор и фото. Детские и взрослые дни рождения.',
 h1='<em>День рождения</em> и вечеринки в Баку',
 lead='Превратим ваш день рождения в незабываемый вечер: DJ, шоумен, игры, лазерное и световое шоу, тематический декор.',
 inc=['DJ и шоумен', 'Лазерное и световое шоу', 'Тематический декор', 'Фото'],
 about=[('DJ и шоумен', 'Музыка и ведущий вместе: игры, конкурсы и танцы — гости участвуют весь вечер.'),
        ('Лазерное и световое шоу', 'За несколько минут превращаем обычный зал в атмосферу клуба.'),
        ('Тематический декор', 'Тема, цвета и детали подбираются под вкус именинника.')],
 venues='Проводили дни рождения в Neolit и других заведениях Баку.',
 wa='Здравствуйте! Хочу узнать о дне рождения.')
PAGES['en']['ad-gunu'] = dict(
 title='Birthday party planning in Baku — DJ, showman and show',
 desc='Birthday and party planning in Baku: DJ, showman, games, laser and light show, themed decor and photo. Kids’ and adults’ birthdays.',
 h1='<em>Birthdays</em> and parties in Baku',
 lead='We turn your birthday into a night to remember: DJ, showman, games, laser and light show, themed decor.',
 inc=['DJ and Showman', 'Laser and light show', 'Themed decor', 'Photo'],
 about=[('DJ and showman', 'Music and hosting together: games, contests and dancing — guests are involved all night.'),
        ('Laser and light show', 'We turn an ordinary hall into a club atmosphere in minutes.'),
        ('Themed decor', 'Theme, colours and details chosen to suit the birthday person.')],
 venues='We have hosted birthdays at Neolit and other venues in Baku.',
 wa='Hello! I would like to know more about a birthday party.')

FAQ = {
 'ru': [('Сколько стоит?', 'Цена зависит от даты, места, количества гостей и выбранной программы. Напишите в WhatsApp или выберите дату на сайте — уточним пакет и точную цену.'),
        ('Звук, свет и декор входят в пакет?', 'В пакеты помолвки, дня рождения, выпускного и корпоратива входит профессиональная звуковая система. Декор, фото-видео и дополнительный свет обсуждаются отдельно — всё от одной команды, не нужно искать разных подрядчиков.'),
        ('Как забронировать дату?', 'Кнопкой «Выбрать дату» на сайте или через WhatsApp: напишите дату, место и тип мероприятия — мы свяжемся с вами.')],
 'en': [('How much does it cost?', 'The price depends on the date, venue, number of guests and the programme you choose. Message us on WhatsApp or pick a date on the site — we will confirm the package and exact price.'),
        ('Are sound, light and decor included?', 'Engagement, birthday, graduation and corporate packages include a professional sound system. Decor, photo-video and extra lighting are agreed separately — all from one team, no need to look for different contractors.'),
        ('How do I book a date?', 'Use the «Pick a date» button on the site or WhatsApp: tell us the date, venue and type of event and we will get back to you.')],
}

SEO = {'ru': {}, 'en': {}}
SEO['ru']['toy'] = {'h2': 'Как проходит организация свадьбы в Баку', 'p': [
 'Организация свадьбы — это десятки деталей одновременно в один день: музыка, ведущий, звук, свет, декор, выход пары, первый танец, торт и настроение гостей. Showband Group берёт всё это на себя одной командой — не нужно искать отдельно певца, DJ, светотехника и декоратора.',
 'Подготовка начинается с выбора даты. Затем знакомимся с площадкой, количеством гостей и вашими пожеланиями и пишем сценарий свадьбы: какая песня звучит в какой момент, когда будут сюрпризы, как чередуются национальные танцы и современная часть. В день свадьбы наша команда в зале от начала до конца и ведёт программу вовремя.',
 'В музыке объединяются живой бэнд, саксофон, нагара, саз и DJ — и национальный, и современный репертуар. Шоумен вовлекает гостей в игры, флешмоб и танцы. Световое шоу, лазер, светящиеся очки и палочки делают финал вечера незабываемым.',
 'Пакеты для свадьбы: Той Диско — 600 AZN (1 час), Mega Disco Show (бэнд + диско) — 800 AZN, Кино-открытие — от 1000 AZN, пакет «Помолвка» — 1500 AZN. Цены для Баку; в районах, в праздничные дни и на некоторых площадках могут отличаться. Выступаем и за рубежом — в любой стране.'],
 'faq': [('За сколько времени нужно обращаться?', 'В сезон (лето и осень) выходные даты быстро заняты, поэтому советуем писать за 1–3 месяца. Если дата свободна, готовимся и в более короткие сроки.'),
         ('Помолвку тоже организуете?', 'Да. Для помолвки и свадьбы готовим программу той же командой — музыка, ведущий, звук-свет и декор.')]}
SEO['en']['toy'] = {'h2': 'How wedding planning works in Baku', 'p': [
 'Planning a wedding means managing dozens of details at once on one day: music, host, sound, light, decor, the couple’s entrance, first dance, cake and the guests’ mood. Showband Group takes all of this on as one team — no need to hire a singer, DJ, lighting crew and decorator separately.',
 'Preparation starts with choosing the date. Then we get to know the venue, the number of guests and your wishes and write the wedding script: which song plays at which moment, when the surprises happen, how national dances and the modern part alternate. On the day our team is in the hall from start to finish and keeps the programme on time.',
 'The music combines a live band, saxophone, naghara, saz and a DJ — both national and modern repertoire. The showman gets guests into games, flash mobs and dancing. A light show, lasers, LED glasses and glow sticks make the finale unforgettable.',
 'Wedding packages: Wedding Disco — 600 AZN (1 hour), Mega Disco Show (band + disco) — 800 AZN, Cinema Opening — from 1000 AZN, Engagement package — 1500 AZN. Prices are for Baku; they may vary in the regions, on holidays and at some venues. We also perform abroad — in any country.'],
 'faq': [('How far in advance should we book?', 'In the summer and autumn season weekend dates fill up fast, so we recommend getting in touch 1–3 months ahead. If the date is free, we can prepare at shorter notice too.'),
         ('Do you organise engagements too?', 'Yes. We prepare engagement and wedding programmes with the same team — music, host, sound and light, and decor.')]}

SEO['ru']['korporativ'] = {'h2': 'Организация корпоративов в Баку', 'p': [
 'Корпоратив — лицо компании: как сотрудники, партнёры и гости запомнят бренд после мероприятия, зависит от организации. Showband Group одной командой организует корпоративные вечера, презентации, новогодние и праздничные программы, юбилеи компаний и церемонии награждения.',
 'Работа начинается с брифа: цель мероприятия, количество гостей, площадка, длительность официальной части и требования бренда. На этой основе готовим сценарий — плавный переход от официальных выступлений к развлекательной части, интерактивные игры, конкурсы и шоу-номера.',
 'Ведущий, Live Band или DJ, звук, свет и лазерное шоу, сцена и декор в цветах бренда — от одной команды. Это снимает проблему координации подрядчиков, и мероприятие проходит вовремя и по плану.',
 'Корпоративный пакет — 2000 AZN, всё включено: подготовка, сценарий, ведущий, тар, певец-гитарист, шоу-бэнд, ритм-ансамбль, часовая дискотека, звук и выезд. Цена для Баку; в регионах и за рубежом может отличаться.'],
 'faq': [('Когда бронировать новогодний корпоратив?', 'Декабрьские даты быстро заняты, поэтому советуем писать за 1–2 месяца.'),
         ('Можно оформить мероприятие в цветах бренда?', 'Да. Сцена, свет, экраны и декор оформляются в цветах и стиле вашего бренда.')]}
SEO['en']['korporativ'] = {'h2': 'Corporate event planning in Baku', 'p': [
 'A corporate event is the face of the company: how employees, partners and guests remember the brand afterwards depends on the organisation. Showband Group organises company parties, presentations, New Year and holiday programmes, company anniversaries and award ceremonies as one team.',
 'Work starts with a brief: the purpose of the event, number of guests, venue, length of the official part and brand requirements. Based on that we prepare the script — a smooth transition from official speeches to entertainment, interactive games, contests and show acts.',
 'Host, Live Band or DJ, sound, light and laser show, stage and decor in your brand colours — from one team. That removes the hassle of coordinating contractors, and the event runs on time and to plan.',
 'Corporate package — 2000 AZN, all inclusive: preparation, script, host, tar, singer-guitarist, show band, rhythm ensemble, 1-hour disco, sound system and travel. The price is for Baku; it may vary in the regions and abroad.'],
 'faq': [('When should we book a New Year corporate party?', 'December dates fill up fast, so we recommend getting in touch 1–2 months ahead.'),
         ('Can you style the event in our brand colours?', 'Yes. Stage, lighting, screens and decor are prepared in your brand colours and style.')]}

SEO['ru']['ad-gunu'] = {'h2': 'Организация дня рождения в Баку', 'p': [
 'Организация дня рождения складывается из мелочей: музыка, ведущий, игры, декор, свет и фото. Showband Group одной командой организует и детские, и взрослые дни рождения, а также вечеринки и выпускные.',
 'Сначала узнаём вкус именинника, количество гостей и площадку, затем строим программу: DJ-сеты, игры и конкурсы шоумена, моменты-сюрпризы, вынос торта и финал. Тематический декор цветами и деталями дополняет стиль праздника.',
 'Лазерное и световое шоу за несколько минут превращает обычный зал в атмосферу клуба. Фотограф снимает лучшие моменты вечера, чтобы день рождения остался не только в памяти, но и на фото.',
 'Пакет «День рождения» — 1000 AZN (ведущий, тар, ритм-инструменты, Showband, DJ и часовая дискотека), пакет «Выпускной и Party» — от 1000 AZN. Цены для Баку; в районах, в праздничные дни и на некоторых площадках могут отличаться.'],
 'faq': [('Детские дни рождения тоже организуете?', 'Да. Для детских дней рождения готовим отдельную программу с играми, ведущим и музыкой по возрасту.'),
         ('Можно провести день рождения в небольшом зале?', 'Да, подбираем звук и свет под размер площадки — ресторан, кафе или другое место.')]}
SEO['en']['ad-gunu'] = {'h2': 'Birthday party planning in Baku', 'p': [
 'Planning a birthday is all about the details: music, host, games, decor, light and photos. Showband Group organises kids’ and adults’ birthdays, as well as parties and graduation nights, as one team.',
 'First we learn the birthday person’s taste, the number of guests and the venue, then we build the programme: DJ sets, the showman’s games and contests, surprise moments, the cake and the finale. Themed decor completes the style with colours and details.',
 'A laser and light show turns an ordinary hall into a club atmosphere in minutes. A photographer captures the best moments so the birthday stays not only in memory but in photos too.',
 'Birthday package — 1000 AZN (host, tar, rhythm instruments, Showband, DJ and a 1-hour disco), Graduation & Party package — from 1000 AZN. Prices are for Baku; they may vary in the regions, on holidays and at some venues.'],
 'faq': [('Do you organise kids’ birthdays?', 'Yes. For kids’ birthdays we prepare a separate programme with age-appropriate games, host and music.'),
         ('Can a birthday be held in a small venue?', 'Yes, we adapt the sound and lighting to the size of the venue — a restaurant, café or any other place.')]}
