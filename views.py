from django.contrib import messages, auth
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect

from .models.cart import Cart
from .models.customer import Customer
from .models.category import Category
from .models.product import Product
from .models.order import OrderDetail


# Create your views here.
def home(request):
    products = None
    totalitem=0
    if request.session.has_key('phone'):
        phone=request.session['phone']
        category = Category.get_all_categories()
        customer=Customer.objects.filter(phone=phone)
        totalitem = len(Cart.objects.filter(phone=phone))
        for c in customer:
            name=c.name
            categoryId = request.GET.get('category')
            if categoryId:
                products = Product.get_all_product_by_category_id(categoryId)
                return render(request, 'index.html', {'product':products})
            else:
                products = Product.get_all_products()
                data = {'product': products, 'category': category,'name':name,'totalitem':totalitem}
                return render(request,'index.html',data)
    else:
        return redirect('login')
    #######################################signup#######################################3

def signup(request):
    if request.method=='GET':
       return render(request,'signup.html')
    else:

        name=request.POST['name']
        phone=request.POST['phone']

        error_message=None
        value={
            'phone':phone,
            'name':name
        }

        customer=Customer(name=name,phone=phone)
        if (not name):
            error_message="Name is required"
        elif not phone:
            error_message="Phone number is required"
        elif len(phone)<10:
            error_message="Phone Number must be 10 character long or more"
        elif customer.isExists():
            error_message="Mobile Number is already exists"
        if not error_message:
            messages.success(request,'congratulations! Registered successfully')
            customer.register()
            return redirect('signup')
        else:
            data={
                'error':error_message,
                'value':value
            }
            return render(request,'signup.html',data)

########################################login#########################################

def login(request):
    if request.method=='GET':
        return render(request,'login.html')
    else:
        phone = request.POST['phone']

        error_message=None
        value={
            'phone':phone
        }
        customer=Customer.objects.filter(phone=request.POST['phone'])
        if customer:
            request.session['phone']=phone
            return redirect('homepage')
        else:
            error_message="invalid credential"
            data={
                'error': error_message,
                'value':value
            }
        return render(request,'login.html',data)
    ###################################product_detail###########################################

def product_detail(request,pk):
    totalitem=0
    product=Product.objects.get(pk=pk)
    item_already_in_cart=False
    if request.session.has_key('phone'):
        phone=request.session['phone']
        totalitem=len(Cart.objects.filter(phone=phone))
        item_already_in_cart=Cart.objects.filter(Q(product=product.id) & Q(phone=phone)).exists()
        customer=Customer.objects.filter(phone=phone)
        for c in customer:
            name=c.name
        data={
            'product':product,
            'item_already_in_cart':item_already_in_cart,
            'name':name,
            'totalitem': totalitem
        }
        return render(request,'product_detail.html',data)
    ####################################logout##############################
def logout(request):
    if request.session.has_key('phone'):
        return redirect('login')
    else:
        return redirect('login')
    ####################################add_to_cart###############################3

def add_to_cart(request):
    phone=request.session['phone']
    product_id=request.GET.get('prod_id')
    product_name=Product.objects.get(id=product_id)
    product=Product.objects.filter(id=product_id)
    for p in product:
        image=p.image
        price=p.price
        Cart(phone=phone,product=product_name,image=image,price=price).save()
        return redirect(f"/product_detail/{product_id}")

    ####################################  show_cart  #############################

def show_cart(request):
    totalitem=0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        totalitem = len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name = c.name
            cart = Cart.objects.filter(phone=phone)
            data={
                'name':name,
                'totalitem':totalitem,
                'cart':cart,
                 }
            if cart:
                return render(request,'show_cart.html',data)
            else:
                return render(request,'empty_cart.html',data)

#############################################  plus cart  #################################################3

def plus_cart(request):
    if request.session.has_key('phone'):
        phone = request.session["phone"]
        product_id=request.GET['prod_id']
        cart=Cart.objects.get(Q(product=product_id) & Q(phone=phone))
        cart.quantity +=1
        cart.save()
        data={
            'quantity':cart.quantity
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.session.has_key('phone'):
        phone = request.session["phone"]
        product_id=request.GET['prod_id']
        cart=Cart.objects.get(Q(product=product_id) & Q(phone=phone))
        cart.quantity -=1
        cart.save()
        data={
            'quantity':cart.quantity
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.session.has_key('phone'):
        phone = request.session["phone"]
        product_id=request.GET['prod_id']
        cart=Cart.objects.get(Q(product=product_id) & Q(phone=phone))
        cart.delete()
        return JsonResponse()

def checkout(request):
    totalitem=0
    if request.session.has_key('phone'):
        phone = request.session["phone"]
        name=request.POST.get('name')
        address= request.POST.get('address')
        mobile = request.POST.get('mobile')
        cart_product=Cart.objects.filter(phone=phone)
        for c in cart_product:
            qty=c.quantity
            price=c.price
            product_name=c.product
            image=c.image
            OrderDetail(user=phone,product_name=product_name,image=image,qty=qty,price=price).save()
            cart_product.delete()
            totalitem = len(Cart.objects.filter(phone=phone))
            customer = Customer.objects.filter(phone=phone)
            for c in customer:
                name = c.name
                data={
                    'name':name,
                    'toatlitem':totalitem
                }

                return render(request,'empty_cart.html',data)
    else:
        return redirect('login')

def orders(request):
    totalitem=0
    if request.session.has_key('phone'):
        phone = request.session["phone"]
        totalitem = len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name = c.name
            order = OrderDetail.objects.filter(user=phone)
            data = {
                'order': order,
                'name': name,
                'totalitem': totalitem

            }
            order = OrderDetail.objects.filter(user=phone)
            if order:
                return render(request, 'orders.html', data)
            else:
                return render(request, 'emptyorders.html', data)
    else:
        return redirect('login')

def search(request):
    totalitem = 0
    if request.session.has_key('phone'):
        phone = request.session["phone"]
        query=request.GET.get('query')
        search=Product.objects.filter(name__contains =query)
        category = Category.get_all_categories()
        totalitem = len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name = c.name
            data={
                'name':name,
                'totalitem':totalitem,
                'category':category,
                'search':search,
                'query':query
            }
            return render(request,'search.html',data)
        else:
            return redirect('login')