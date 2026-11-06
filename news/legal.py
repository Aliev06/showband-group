#!/usr/bin/env python3
"""Showband Group — hüquqi səhifələr: /privacy/ və /terms/ (TikTok tətbiqi üçün tələb olunur).
build_news.py tərəfindən çağırılır."""
from build_news import head, foot, SITE, w

CSS = '''<style>
.lg{max-width:780px;padding-top:24px}
.lg h1{font:900 clamp(30px,4vw,48px)/1.08 var(--d);letter-spacing:-.03em;margin:16px 0 8px}
.lg h2{font:700 20px/1.3 var(--d);margin:34px 0 10px}
.lg p,.lg li{color:#d8d8de;line-height:1.7}
.lg .upd{color:var(--mute);font-size:14px}
.lg hr{border:0;border-top:1px solid var(--line);margin:44px 0}
</style>'''

UPD = '7 noyabr 2026 / 7 November 2026'
CONTACT = 'WhatsApp / telefon: +994 55 611 87 87 · showbandgroup.az'

PRIVACY = f'''
 <section class="lg">
  <span class="chip">Showband Group</span>
  <h1>Məxfilik siyasəti</h1>
  <p class="upd">Yenilənib: {UPD}</p>
  <p>Bu səhifə Showband Group-un saytının (showbandgroup.az) və daxili məzmun alətinin («Showband Bot») hansı məlumatları necə istifadə etdiyini izah edir.</p>
  <h2>Hansı məlumatları toplayırıq</h2>
  <ul>
   <li><b>Bron formu:</b> adınız, telefon nömrəniz, tədbir tarixi və növü. Bu məlumatlar yalnız WhatsApp vasitəsilə bizə göndərilir və saytda saxlanılmır.</li>
   <li><b>TikTok inteqrasiyası:</b> «Showband Bot» yalnız Showband Group-un öz TikTok hesabına qoşulur. Alət TikTok-dan hesabın əsas profil məlumatlarını (ad, avatar) alır və hazır videoları həmin hesabın qaralamalarına (inbox) yükləmək icazəsindən istifadə edir.</li>
  </ul>
  <h2>Məlumatlardan necə istifadə edirik</h2>
  <p>Bron məlumatları yalnız sizinlə əlaqə saxlamaq üçün istifadə olunur. TikTok giriş tokenləri yalnız Showband Group-un videolarını onun öz hesabına yükləmək üçün istifadə olunur, şifrələnmiş şəkildə saxlanılır və heç kimə ötürülmür.</p>
  <h2>Üçüncü tərəflər</h2>
  <p>Məlumatlarınızı satmırıq və reklam məqsədilə paylaşmırıq. Sayt GitHub Pages və Cloudflare üzərində işləyir; video yükləmə üçün TikTok Content Posting API istifadə olunur.</p>
  <h2>Məlumatların silinməsi</h2>
  <p>TikTok inteqrasiyasına verilən icazəni istənilən vaxt TikTok tətbiqində (Parametrlər → Təhlükəsizlik → İcazələr) ləğv edə bilərsiniz. Digər məlumatların silinməsi üçün bizimlə əlaqə saxlayın.</p>
  <h2>Əlaqə</h2>
  <p>{CONTACT}</p>
  <hr>
  <h1>Privacy Policy</h1>
  <p class="upd">Last updated: {UPD}</p>
  <p>This page explains what information the Showband Group website (showbandgroup.az) and its internal content tool (“Showband Bot”) use and how.</p>
  <h2>Information we collect</h2>
  <ul>
   <li><b>Booking form:</b> your name, phone number, event date and type. This is sent to us via WhatsApp only and is not stored on the website.</li>
   <li><b>TikTok integration:</b> Showband Bot connects only to Showband Group’s own TikTok account. It reads the account’s basic profile info (name, avatar) and uses the permission to upload finished videos to that account’s drafts (inbox).</li>
  </ul>
  <h2>How we use it</h2>
  <p>Booking details are used only to contact you. TikTok access tokens are used only to upload Showband Group’s own videos to its own account; they are stored encrypted and never shared.</p>
  <h2>Third parties</h2>
  <p>We do not sell or share your data for advertising. The website runs on GitHub Pages and Cloudflare; video uploads use the TikTok Content Posting API.</p>
  <h2>Data deletion</h2>
  <p>You can revoke the TikTok permission at any time in the TikTok app (Settings → Security → Permissions). To delete any other data, contact us.</p>
  <h2>Contact</h2>
  <p>{CONTACT}</p>
 </section>
'''

TERMS = f'''
 <section class="lg">
  <span class="chip">Showband Group</span>
  <h1>İstifadə şərtləri</h1>
  <p class="upd">Yenilənib: {UPD}</p>
  <p>showbandgroup.az saytı Showband Group-a məxsusdur. Saytdakı mətnlər, foto və videolar Showband Group-un mülkiyyətidir və icazəsiz kommersiya məqsədilə istifadə edilə bilməz.</p>
  <h2>Qiymətlər və bron</h2>
  <p>Saytda göstərilən qiymətlər məlumat xarakterlidir. Dəqiq qiymət tədbirin tarixi, məkanı və proqramına görə razılaşdırılır. Bron yalnız Showband Group tərəfindən təsdiqləndikdən sonra qüvvəyə minir.</p>
  <h2>«Showband Bot» aləti</h2>
  <p>Showband Bot Showband Group-un daxili alətidir və yalnız şirkətin öz sosial şəbəkə hesablarında (o cümlədən TikTok) öz videolarını hazırlamaq və qaralamalara yükləmək üçün istifadə olunur. Paylaşım qərarını hər dəfə hesab sahibi verir.</p>
  <h2>Məsuliyyət</h2>
  <p>Saytdakı xəbərlər açıq mənbələrə əsaslanır və mənbə göstərilir. Xarici saytların məzmununa görə məsuliyyət daşımırıq.</p>
  <h2>Əlaqə</h2>
  <p>{CONTACT}</p>
  <hr>
  <h1>Terms of Service</h1>
  <p class="upd">Last updated: {UPD}</p>
  <p>The website showbandgroup.az belongs to Showband Group. Texts, photos and videos on the site are the property of Showband Group and may not be used commercially without permission.</p>
  <h2>Prices and booking</h2>
  <p>Prices on the website are indicative. The final price is agreed based on the event date, venue and programme. A booking is valid only after confirmation by Showband Group.</p>
  <h2>Showband Bot</h2>
  <p>Showband Bot is Showband Group’s internal tool. It is used only to prepare the company’s own videos and upload them to the drafts of the company’s own social accounts (including TikTok). The account owner decides on every publication.</p>
  <h2>Liability</h2>
  <p>News on the site is based on public sources, which are credited. We are not responsible for the content of external websites.</p>
  <h2>Contact</h2>
  <p>{CONTACT}</p>
 </section>
'''


def page(slug, title, desc, body):
    rel = '../'
    return head(title, desc, f'{SITE}/{slug}/', rel, 'website', CSS).replace(
        f'<a class="on" href="{rel}xeberler/">', f'<a href="{rel}xeberler/">') + body + foot(rel)


def build():
    w('privacy/index.html', page('privacy', 'Məxfilik siyasəti — Privacy Policy | Showband Group',
                                 'Showband Group saytı və Showband Bot alətinin məxfilik siyasəti. Privacy Policy of Showband Group.', PRIVACY))
    w('terms/index.html', page('terms', 'İstifadə şərtləri — Terms of Service | Showband Group',
                               'Showband Group saytının və Showband Bot alətinin istifadə şərtləri. Terms of Service.', TERMS))


if __name__ == '__main__':
    build()
