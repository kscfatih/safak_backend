from django.db import models

# Create your models here.

class OpportunityProduct(models.Model):
    name = models.CharField(max_length=200, verbose_name="Ürün Adı")
    description = models.TextField(verbose_name="Açıklama")
    original_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Orijinal Fiyat"
    )
    discounted_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="İndirimli Fiyat"
    )
    image = models.ImageField(
        upload_to='opportunity_products/',
        verbose_name="Ürün Resmi",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Fırsat Ürünü"
        verbose_name_plural = "Fırsat Ürünleri"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def discount_percentage(self):
        """İndirim yüzdesini hesaplar"""
        if self.original_price > 0:
            return int(((self.original_price - self.discounted_price) / self.original_price) * 100)
        return 0
    
    @property
    def savings_amount(self):
        """Tasarruf edilen miktarı hesaplar"""
        return self.original_price - self.discounted_price
