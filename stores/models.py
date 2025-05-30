from django.db import models
import uuid
from users.models import Profile
import secrets
from . paystack import Paystack

# :::: CATEGORY MODEL :::::
class Category(models.Model):
    title = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# :::: PRODUCT MODEL :::::
class Product(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=9, decimal_places=2)
    discount_price = models.DecimalField(max_digits=9, decimal_places=2, null=True,blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='stores')
    photo1 = models.ImageField(upload_to='stores', null=True, blank=True)
    photo2 = models.ImageField(upload_to='stores', null=True, blank=True)
    photo3 = models.ImageField(upload_to='stores', null=True, blank=True)
    photo4 = models.ImageField(upload_to='stores', null=True, blank=True)
    photo5 = models.ImageField(upload_to='stores', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    in_stock = models.IntegerField()
    product_id = models.UUIDField(unique=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    def save(self,*args,**kwargs):
        if not self.product_id:
            self.product_id = uuid.uuid4()
        super().save(*args,**kwargs)


# :::: CART MODEL :::::
class Cart(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True,blank=True)
    total = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart - {str(self.total)}'


# :::: CART PRODUCT MODEL :::::
class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Cart Product - {self.cart.id} - {self.quantity}'
    

# :::: ORDER MODEL :::::
ORDER_STATUS=(
    ('pending','pending'),
    ('complete','complete'),
    ('cancel','cancel')
)
PAYMENT_METHOD=(
    ('paystack','paystack'),
    ('paypal','paypal'),
    ('stripe','stripe'),
    ('bank','bank')
)
class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    order_by = models.CharField(max_length=255)
    shipping_address = models.TextField()
    mobile = models.CharField(max_length=50)
    email = models.EmailField()
    amount = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50,choices=ORDER_STATUS,default='pending')
    payment_method = models.CharField(max_length=50,choices=PAYMENT_METHOD, default='paystack')
    payment_complete = models.BooleanField(default=False)
    ref = models.CharField(max_length=255,null=True,unique=True)
    
    def __str__(self):
        return f'{self.amount} -  {str(self.id)}'
    
    # auto save ref
    def save(self,*args,**kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50) #123
            obj_with_sm_ref = Order.objects.filter(ref = ref).exists()
            if not obj_with_sm_ref:
                self.ref = ref
        super().save(*args,**kwargs)
    
    # amount from cent/kobo to naira/dolla
    def amount_value(self)->int:
        return self.amount * 100
    
    # verify payment
    def verify_payment(self):
        paystack = Paystack()
        status,result = paystack.verify_payment(self.ref)
        if status and result.get('status') == 'success':
            # ensure the amount match
            if result['amount']/100 == self.amount:
                self.payment_complete == True
                self.cart.delete()
                self.save()
                return True
            return False


