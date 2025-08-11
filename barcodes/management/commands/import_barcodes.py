from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from barcodes.models import CampaignBarcode
import os
import re


class Command(BaseCommand):
    help = 'Txt dosyasından barkodları içe aktar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Barkodların bulunduğu txt dosyasının yolu'
        )
        parser.add_argument(
            '--campaign-code',
            type=str,
            required=True,
            help='Kampanya kodu'
        )
        parser.add_argument(
            '--barcode-name',
            type=str,
            default='Kampanya Barkodu',
            help='Barkod adı (varsayılan: "Kampanya Barkodu")'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        campaign_code = options['campaign_code']
        barcode_name = options['barcode_name']

        # Dosya varlığını kontrol et
        if not os.path.exists(file_path):
            raise CommandError(f'Dosya bulunamadı: {file_path}')

        self.stdout.write(f'📁 Dosya okunuyor: {file_path}')
        self.stdout.write(f'🏷️  Kampanya Kodu: {campaign_code}')
        self.stdout.write(f'📝 Barkod Adı: {barcode_name}')

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Satırları temizle ve 6 haneli kodları filtrele
            barcodes = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue

                # 6 haneli sayı kontrolü
                if re.match(r'^\d{6}$', line):
                    barcodes.append(line)
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Satır {line_num}: Geçersiz format "{line}" (6 haneli sayı olmalı)'
                        )
                    )

            self.stdout.write(f'✅ {len(barcodes)} adet geçerli barkod bulundu')

            if not barcodes:
                self.stdout.write(self.style.ERROR('❌ Hiç geçerli barkod bulunamadı!'))
                return

            # Veritabanı işlemleri
            with transaction.atomic():
                created_count = 0
                duplicate_count = 0
                error_count = 0

                for barcode_code in barcodes:
                    try:
                        # Daha önce eklenmiş mi kontrol et
                        if CampaignBarcode.objects.filter(barcode_code=barcode_code).exists():
                            duplicate_count += 1
                            continue

                        # Yeni barkod oluştur
                        campaign_barcode = CampaignBarcode.objects.create(
                            barcode_code=barcode_code,
                            barcode_name=f"{barcode_name} - {barcode_code}",
                            campaign_code=campaign_code,
                            is_assigned=False,
                            is_active=True
                        )

                        # Barkod görüntüsünü oluştur
                        if campaign_barcode.generate_barcode_image():
                            campaign_barcode.save()
                            created_count += 1
                            
                            # Her 100 kayıtta bir ilerleme göster
                            if created_count % 100 == 0:
                                self.stdout.write(f'📊 {created_count} barkod oluşturuldu...')
                        else:
                            error_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'⚠️  {barcode_code}: Barkod görüntüsü oluşturulamadı')
                            )

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'❌ {barcode_code}: Hata - {str(e)}')
                        )

            # Sonuçları göster
            self.stdout.write('\n' + '='*50)
            self.stdout.write('📊 İÇE AKTARMA RAPORU')
            self.stdout.write('='*50)
            self.stdout.write(f'✅ Başarıyla oluşturulan: {created_count}')
            self.stdout.write(f'⚠️  Zaten mevcut olanlar: {duplicate_count}')
            self.stdout.write(f'❌ Hatalı olanlar: {error_count}')
            self.stdout.write(f'📁 Toplam işlenen: {len(barcodes)}')
            self.stdout.write('='*50)

            if created_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'🎉 {created_count} adet barkod başarıyla içe aktarıldı!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  Hiç yeni barkod eklenmedi.')
                )

        except FileNotFoundError:
            raise CommandError(f'Dosya bulunamadı: {file_path}')
        except PermissionError:
            raise CommandError(f'Dosya okuma izni yok: {file_path}')
        except Exception as e:
            raise CommandError(f'Beklenmeyen hata: {str(e)}')

        self.stdout.write('\n✨ İşlem tamamlandı!')