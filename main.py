from playwright.sync_api import sync_playwright
from ctypes import windll
from requests import post


dosya_yolu = "accounts.txt"

WEBHOOK_URL = "DISCORD-WEBHOOK"


with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.set_default_timeout(10000)

    with open(dosya_yolu, "r") as dosya:
        hesaplar = dosya.readlines()

    aktif_hesap_sayisi = 0
    yasakli_hesap_sayisi = 0
    hata_hesap_sayisi = 0
    toplam_hesap_sayisi = len(hesaplar)
    kalan_hesap_sayisi = len(hesaplar)

    with open("aktif.txt", "w") as results_file, open("yasakli.txt", "w") as banned_file, open("error.txt", "w") as error_file:
        for hesap in hesaplar:
            hesap = hesap.strip()
            hesap_sayfasi_url = f"https://www.twitch.tv/{hesap}"

            try:
                page.goto(hesap_sayfasi_url, wait_until="load")

                inner_text = page.inner_text("body", timeout=1000)
                if "Bu kanal, Twitch'in Topluluk İlkeleri veya Hizmet Koşullarının ihlali nedeniyle şu an için hizmet dışı." not in inner_text:
                    if "Üzgünüz. Bir zaman makinesine sahip değilseniz bu içerik artık ulaşılamaz demektir." in inner_text:
                        hata_hesap_sayisi += 1
                        kalan_hesap_sayisi -= 1
                        print(f"{hesap}: \033[91mHATALI\033[0m")
                        error_file.write(hesap + "\n")
                        post(url=WEBHOOK_URL, json={"content": f"```diff\n- HATALI\n+ HESAP: {hesap}\n```"})
                    else:
                        aktif_hesap_sayisi += 1
                        kalan_hesap_sayisi -= 1
                        print(f"{hesap}: \033[92mAKTIF\033[0m")
                        results_file.write(hesap + "\n")
                else:
                    yasakli_hesap_sayisi += 1
                    kalan_hesap_sayisi -= 1
                    print(f"{hesap}: \033[31mYASAKLI\033[0m")
                    banned_file.write(hesap + "\n")
                    post(url=WEBHOOK_URL, json={"content": f"```diff\n- YASAKLI\n+ HESAP: {hesap}\n```"})
            except Exception as e:
                hata_hesap_sayisi += 1
                kalan_hesap_sayisi -= 1
                print(f"{hesap}: Sayfa yüklenirken bir hata oluştu: {str(e)}")
                error_file.write(hesap + "\n")

            windll.kernel32.SetConsoleTitleW(f"Ban Checker | SON: {hesap} | AKTIF: {aktif_hesap_sayisi} | YASAKLI: {yasakli_hesap_sayisi} | HATALI: {hata_hesap_sayisi} | KALAN: {kalan_hesap_sayisi}/{toplam_hesap_sayisi}")

    browser.close()

    post(url=WEBHOOK_URL, json={"content": f"```diff\n+ TOPLAM: {toplam_hesap_sayisi}\n+ AKTIF: {aktif_hesap_sayisi}\n- YASAKLI: {yasakli_hesap_sayisi}\n- HATALI: {hata_hesap_sayisi}\n```"})
    print(f"\n\033[93mTOPLAM\033[0m: {toplam_hesap_sayisi}")
    print(f"\033[92mAKTIF\033[0m: {aktif_hesap_sayisi}")
    print(f"\033[31mYASAKLI\033[0m: {yasakli_hesap_sayisi}")
    print(f"\033[91mHATALI\033[0m: {hata_hesap_sayisi}")

    print("\nKapatmak için enter'a bas.")
    input()
