from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from django.core.mail import send_mail
from . models import *
from . forms import *
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime


# Create your views here.
def index(request):
    context={}
    form=Enquiry_form()

    if request.method=="POST":
        if'save' in request.POST:
            name=request.POST.get('name')
            email=request.POST.get('email')
            phone=request.POST.get('phone')
            message=request.POST.get('message')
            branch=request.POST.get('branch')
            branch_name=Branch.objects.get(name=branch)
            enquiries=Enquiry.objects.create(name=name,email=email,phone=phone,message=message,branch=branch_name)
            enquiries.save()
            messages.success(request,'Enquiries submitted successfully')


    enquiry=Enquiry.objects.all()
    package=Package.objects.all()
    branch=Branch.objects.all()
    testimonial=Testimonial.objects.all()
    context['testimonial']=testimonial
    context['enquiry']=enquiry
    context['form']=form
    context['package']=package
    context['branch']=branch

    return render(request,'index.html',context)




def about(request):
    context={}
    package=Package.objects.all()
    context['package']=package
    return render(request,'about.html',context)

def package(request):
    context={}


    package=Package.objects.all()
    context['package']=package
    return render(request,'packages.html',context)


@login_required(login_url='login')
def packages_view(request,name):
    context={}
    
    branch=Branch.objects.all()
    package=Package.objects.all()
    subpackage=Subpackage.objects.all()
    context['subpackage']=subpackage
    context['package']=package
    context['branch']=branch
    context['data']=Package.objects.get(name=name)
    return render(request,'package_view.html',context)


def order_payment(request,name):
    if request.method == "POST":
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        pack_name = request.POST.get("package_name")
        package_name = Package.objects.get(name=pack_name)
        bran_name = request.POST.get("branch_name")
        branch_name= Branch.objects.get(name=bran_name)
        us_name = request.POST.get("username")
        username = User.objects.get(username=us_name)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
            name=name, amount=amount, provider_order_id=razorpay_order["id"], package_name=package_name, branch_name=branch_name,username=username,
        )
        order.save()
        subpackage=Subpackage.objects.all()
        return render(
            request,
            "package_view.html",
            {
                "callback_url": "http://" + "127.0.0.1:8000" + "/razorpay/callback/",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
                "data": Package.objects.get(name=package_name),
                "subpackage": subpackage
            },
        )
   
    return redirect('package_view',name=name)



@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if not verify_signature(request.POST):
            order.status = PaymentStatus.FAILURE
            order.save()
            messages.success(request,'Payment failed. Please Try again')
            return redirect('packages_view', name=order.package_name)
              # callback giving html page
            #  or  return redirect(function name of callback giving html page)
        else:
            order.status = PaymentStatus.SUCCESS
            order.save()
            messages.success(request,'Payment Successfull')
            return redirect('packages_view', name=order.package_name) # callback giving html page
            #  or  return redirect(function name of callback giving html page)

    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()
        messages.success(request,'Payment failed. Please Try again')
        return redirect('packages_view', name=order.package_name)

          # callback giving html page
        #  or  return redirect(function name of callback giving html page)
        






def blog(request):
    context={}


    package=Package.objects.all()
    context['package']=package
    return render(request,'blog.html',context)

def branches(request):
    context={}

    branch=Branch.objects.all()
    context['branch']=branch

    return render(request,'branches.html',context)


def branches_view(request,name):
    context={}

   

    branch=Branch.objects.all()
    timing=Branch_time.objects.all()
    context['timing']=timing
    context['branch']=branch
    context['data']=Branch.objects.get(name=name)
    return render(request,'branch_view.html',context)


def branches_package_view(request, name):
    context = {}
    
    package=Package.objects.all()
    branch=Branch.objects.all()
    subpackage = Subpackage.objects.all()
    context['subpackage'] = subpackage
    context['branch'] = branch
    context['package'] = package
    context['data'] =Package.objects.get(name=name)

    return render(request, 'branch_package_view.html', context)


def branch_packages(request,name):
    context={}

    branch=Branch.objects.all()
    package=Package.objects.all()
    subpackage=Subpackage.objects.all()
    context['subpackage']=subpackage
    context['package']=package
    context['branch']=branch
    context['data']=Branch.objects.get(name=name)
    return render(request,'branch_package.html',context)



def gallery(request):
    context={}


    package=Package.objects.all()
    gallery=Gallery.objects.all()
    context['package']=package
    context['gallery']=gallery
    return render(request,'gallery.html',context)



  
def moleculor_biology(request):
    context={}


    package=Package.objects.all()
    context['package']=package
    return render(request,'moleculor-biology.html',context)

def radiology(request):
    context={}


    package=Package.objects.all()
    context['package']=package
    return render(request,'radiology.html',context)

def test(request):
    context={}


    package=Package.objects.all()
    context['package']=package
    return render(request,'test.html',context)

def contact(request):
    context={}
    form=Contact_form()

    if request.method=="POST":
        if'save' in request.POST:
            name=request.POST.get('name')
            email=request.POST.get('email')
            phone=request.POST.get('phone')
            subject=request.POST.get('subject')
            message=request.POST.get('message')
            branch=request.POST.get('branch')
            branch_name=Branch.objects.get(name=branch)
            contacts=Contact.objects.create(name=name,email=email,phone=phone,subject=subject,message=message,branch=branch_name)
            contacts.save()
            messages.success(request,"Message send successfully")

          
    
   

    package=Package.objects.all()
    branch=Branch.objects.all()
    context['branch']=branch
    context['package']=package
    contact=Contact.objects.all()
    context['contact']=contact
    context['form']=form
    return render(request,'contact-us.html',context)


@login_required(login_url='login')
def appointment(request):
    context = {}
    form = Appointment_form()

    if request.method == "POST":
        if 'save' in request.POST:
            name=request.POST.get('name')
            email=request.POST.get('email')
            phone=request.POST.get('phone')
            date=request.POST.get('date')
            time=request.POST.get('time')
            age=request.POST.get('age')
            gender=request.POST.get('gender')
            address=request.POST.get('address')
            message=request.POST.get('message')
            branch_name=request.POST.get('branch')
            branch=Branch.objects.get(name=branch_name)
            appointment=Appointment.objects.create(name=name,email=email,phone=phone,date=date,time=time,age=age,gender=gender,address=address,message=message,branch=branch)
            appointment.save()
            messages.success(request,'Appointment Booked Successfully')





    appointments = Appointment.objects.all()
    branch = Branch.objects.all()
    context['branch'] = branch
    context['appointments'] = appointments
    context['form'] = form
    return render(request, 'appointment.html', context)


def department(request):
    return render(request,'department.html')

def privacy_policy(request):
    return render(request,'privacy.html')

def terms_conditions(request):
    return render(request,'terms.html')

def testimonials(request):
    context={}
    form=Testimonial_form()

    if request.method=="POST":
        if'post' in request.POST:
                name = request.POST.get('name')
                branch_name = request.POST.get('branch')
                review = request.POST.get('review')
                branch = Branch.objects.get(name=branch_name)
                reviews = Testimonial.objects.create(name=name, branch=branch, review=review)
                reviews.save()
                messages.success(request, 'Testimonial Posted Successful')
                return redirect('testimonials')
    

    testimonial=Testimonial.objects.all()
    branch=Branch.objects.all()
    context['branch']=branch
    context['testimonial']=testimonial
    context['form']=form
    return render(request,'testimonial.html',context)

def register(request):
    if 'user' in request.session:
        data=User.objects.get(username=request.session['user'])
        data.email
    if request.method=="POST":
        fname=request.POST['fname']
        lname=request.POST['lname']
        uname=request.POST['uname']
        email=request.POST['email']
        password=request.POST['password']
        if User.objects.filter(username=uname).exists():
            messages.error(request, 'Username already exists. Please choose a different username.')
            return render(request, 'registration/register.html')
        user=User.objects.create_user(first_name=fname,last_name=lname,username=uname,email=email,password=password)
        user.save()
        messages.success(request,'Registration Successfull')
        subject = 'Welcome to GMRL Laboratories'
        message = f'Hi {user.username}, Thank you for registering.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email, ]
        send_mail( subject, message, email_from, recipient_list )
        return redirect('login')
    return render(request,'registration/register.html')
       
    
def login(request):
    if request.method == "POST":
        uname = request.POST.get('uname')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=uname, password=password)
        
        if user:
            auth.login(request, user)
            messages.success(request, 'Login successful')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'registration/login.html')
    else:
        return render(request, 'registration/login.html')
    
def logout(request):
    auth.logout(request)
    request.session.flush()
    return redirect('index')


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('index')






@login_required(login_url='login')
def profile(request):
    context={}
    form=Profile_form()

    if request.method=="POST":      

        if'save' in request.POST:
            fname=request.POST.get('name')
            uname=request.POST.get('username')
            username=User.objects.get(username=uname)
            email=request.POST.get('email')
            age=request.POST.get('age')
            number=request.POST.get('number')
            gender=request.POST.get('gender')
            address=request.POST.get('address')
            date=request.POST.get('date')
            
            profile=Profile.objects.create(name=fname,username=username,email=email,age=age,number=number,gender=gender,address=address,date=date)
            profile.save()
            messages.success(request, 'Profile Registration Successful')
      
        if'delete' in request.POST:
            key=request.POST.get('delete')
            profile=Profile.objects.get(id=key)
            profile.delete()
            return redirect('profile')
            
# Retrieve the current logged-in user object
    user = request.user
    
    try:
            
            # Retrieve the profile associated with the logged-in user
            profiles = Profile.objects.get(username=user)
            context['profiles'] = profiles
    except Profile.DoesNotExist:
            # Handle the case where the profile doesn't exist
            profiles = None

    package=Package.objects.all()
    profile=Profile.objects.all()
    context['profile'] = profile
    context['package']=package
    context['form'] = form

    return render(request,'user_profile/profile.html',context)

def profile_update(request):
    context={}
    form=Profile_form()

    if 'update' in request.POST:
        key = request.POST.get('update')
        profile = Profile.objects.get(id=key)
        name = request.POST['name']
        email = request.POST['email']
        age = request.POST['age']
        date = request.POST['date']
        address = request.POST['address']
        gender = request.POST['gender']
        number = request.POST['number']
        user_name = request.POST['username']
        profile_user = User.objects.get(username=user_name)
        profile.name = name
        profile.age = age
        profile.email = email
        profile.date = date
        profile.address = address
        profile.gender = gender
        profile.username = profile_user
        profile.number = number
        profile.save()
        return redirect('profile')
    

    user = request.user
        
    try:
            
            # Retrieve the profile associated with the logged-in user
            profiles = Profile.objects.get(username=user)
            context['profiles'] = profiles
    except Profile.DoesNotExist:
            # Handle the case where the profile doesn't exist
            profiles = None

    profile=Profile.objects.all()
    package=Package.objects.all()
    context['package']=package
    context['profile'] = profile
    context['form'] = form

    return render(request,'user_profile/profile_update.html',context)



def admin_page(request):

    context={}

    package=Package.objects.all()
    context['package']=package


    pack_count=0
    for i in package:
        if i.branch.status:
            pack_count += 1


    context['pack_count']=pack_count

    order=Order.objects.all()
    context['order']=order
    total_order=len(order)
    context['total_order']=total_order
    total_amount=0


    for i in order:
        total_amount+=i.amount

    context['total_amount']=total_amount

    branch=Branch.objects.all()

    branch_count=0
    for i in branch:
        if i.status:
            branch_count += 1
  
    context['branch_count']=branch_count

    branches = Branch.objects.filter(status=True)
    packages = Package.objects.all()
    
    branch_package_count = {}

    # Loop through branches and initialize package count for each branch
    for branch in branches:
        branch_package_count[branch.name] = 0

    # Loop through packages and increment package count for each branch
    for package in packages:
        branch_name = package.branch.name
        # Check if the branch's status is False, if so, continue to the next package
        if not package.branch.status:
            continue
        branch_package_count[branch_name] += 1

    # Create a list of dictionaries containing branch name and package count
    branches_with_counts = [{'name': branch.name, 'count': branch_package_count[branch.name]} for branch in branches]

    context['branches_with_counts'] = branches_with_counts

    appointment = Appointment.objects.all()
    context['appointment']=appointment

    contact = Contact.objects.all()
    context['contact']=contact

    enquiry = Enquiry.objects.all()
    context['enquiry']=enquiry
    
    return render(request,'admin_page/admin_page.html',context)


def admin_branches(request):
    context = {}
    form = Branch_form()

    if request.method == "POST":
        if'save' in request.POST:
            form=Branch_form(request.POST)
            if form.is_valid():
                form.save()
            else:
                print(messages.error)
                 
        if'delete' in request.POST:
            key = request.POST.get('delete')
            branch = Branch.objects.get(id=key)
            branch.delete()

        if'update' in request.POST:
            key = request.POST.get('update')
            branch = Branch.objects.get(id=key)
            form=Branch_form(request.POST,instance=branch)
            if form.is_valid():
                form.save()


    branch = Branch.objects.all()
    context['branch'] = branch
    context['form'] = form
    return render(request, 'admin_page/admin_branches.html', context)



def admin_branch_view(request,name):
    context = {}
    timing_form=Branch_timing_form()

    if request.method == "POST":
        bran=request.POST.get('name')
        branch_name = Branch.objects.get(name=bran)
        opening_hours=request.POST.get('opening_hours')
        closing_hours=request.POST.get('closing_hours')
        opening_week=request.POST.get('opening_week')
        closing_week=request.POST.get('closing_week')
        timing = Branch_time.objects.create(name=branch_name, opening_hours=opening_hours,closing_hours=closing_hours,opening_week=opening_week,closing_week=closing_week)
        timing.save()
   
     

    branch = Branch.objects.all()
    package=Package.objects.all()
    timing=Branch_time.objects.all()
    context['timing']=timing
    context['package']=package
    context['branch'] = branch
    context['timing_form'] = timing_form
    context['data'] = Branch.objects.get(name=name)

    return render(request, 'admin_page/admin_branch_view.html', context)



def admin_packages(request):
    context = {}
    form = Package_add()

    if request.method == "POST":
        if 'save' in request.POST:
                name = request.POST.get('name')
                image = request.POST.get('image')
                price = request.POST.get('price')
                branch_name = request.POST.get('branch')
                branch = Branch.objects.get(name=branch_name)
                pack = Package.objects.create(name=name, image=image, price=price, branch=branch)
                pack.save()

          

                        
                 
        if 'delete' in request.POST:
            key = request.POST.get('delete')
            package = Package.objects.get(id=key)
            package.delete()

        if'update' in request.POST:
            key = request.POST.get('update')
            package = Package.objects.get(id=key)
            name=request.POST['name']
            image=request.POST['image']
            price=request.POST['price']
            branch_name=request.POST['branch']
            branch = Branch.objects.get(name=branch_name)
            package.name=name
            package.price=price
            package.image=image
            package.branch=branch
            package.save()
            


           
            
    package = Package.objects.all()
    context['package'] = package
    context['form'] = form
    return render(request, 'admin_page/admin_packages.html', context)




def admin_package_view(request, name):
    context = {}
    form = Subpackage_form()
    if request.method == "POST":
        if'save' in request.POST:
            pack_content = request.POST.get('content')
            pack_name = Package.objects.get(name=name)
            subpack = Subpackage.objects.create(name=pack_name, content=pack_content)
            subpack.save()
        
        if 'delete' in request.POST:
            key = request.POST.get('delete')
            subpackage = Subpackage.objects.get(id=key)
            subpackage.delete()

        if'update' in request.POST:
            key = request.POST.get('update')
            subpackage=Subpackage.objects.get(id=key)
            pack_content = request.POST['content']
            pack_name = Package.objects.get(name=name)
            subpackage.name=pack_name
            subpackage.content=pack_content
            subpackage.save()

        
        
                

    
           

    subpackage = Subpackage.objects.all()
    context['subpackage'] = subpackage
    context['form'] = form
    context['data'] = Package.objects.get(name=name)

    return render(request, 'admin_page/admin_package_view.html', context)



def admin_package_add(request):
    return render(request,'admin_page/admin_package_add.html')

def admin_package_update(request):
    return render(request,'admin_page/admin_package_update.html')

def admin_appointments_view(request):
    context = {}

    appointments = Appointment.objects.all()
    branches = Branch.objects.all()

    # Check if the filter button is pressed
    if 'branch' in request.GET:
        # Get the selected branch name from the request
        branch_name = request.GET.get('branch')

        # If a branch name is selected, filter appointments based on it
        if branch_name:
            appointments = appointments.filter(branch__name=branch_name)

        context['selected_branch'] = branch_name

    # Check if the filter button for date is pressed
    if 'date' in request.GET:
        # Get the selected date from the request
        selected_date_str = request.GET.get('date')

        # If a date is selected, convert it to datetime format
        if selected_date_str:
            selected_date = datetime.strptime(selected_date_str, '%B %d, %Y')

            # Filter appointments based on the selected date
            appointments = appointments.filter(date=selected_date)

        context['selected_date'] = selected_date_str

    context['branches'] = branches
    context['appointments'] = appointments

    return render(request, 'admin_page/admin_appointments_view.html', context)

def admin_appointment_detail(request):
    context={}

    if request.method == "POST":
        appointment_id=request.POST.get('id')

        context['data']=Appointment.objects.get(id=appointment_id)

    return render(request,'admin_page/admin_appointment_detail.html',context)


def admin_contacts_view(request):
    context={}

    branches=Branch.objects.all()
    contact=Contact.objects.all()

    if 'branch' in request.GET:

        branch_name = request.GET.get('branch')
        if branch_name:
            contact = Contact.objects.filter(branch__name=branch_name)
        context['selected_branch'] = branch_name

    context['contact'] = contact  # Assuming you want to pass the filtered enquiries to the context
    context['branches'] = branches


    return render(request,'admin_page/admin_contacts_view.html',context)

def admin_contact_detail(request):
    context={}

    if request.method == "POST":
        contact_id=request.POST.get('id')

        context['data']=Contact.objects.get(id=contact_id)

    return render(request,'admin_page/admin_contact_detail.html',context)


def admin_enquiries_view(request):
    context={}

    branches=Branch.objects.all()
    enquiry=Enquiry.objects.all()

    if 'branch' in request.GET:

        branch_name = request.GET.get('branch')
        if branch_name:
            enquiry = Enquiry.objects.filter(branch__name=branch_name)
        context['selected_branch'] = branch_name

    context['enquiry'] = enquiry  # Assuming you want to pass the filtered enquiries to the context
    context['branches'] = branches


    return render(request,'admin_page/admin_enquiries_view.html',context)


def admin_enquiry_detail(request):

    context={}

    if request.method == "POST":
        enquiry_id=request.POST.get('id')

        context['data']=Enquiry.objects.get(id=enquiry_id)


    return render(request, 'admin_page/admin_enquiry_detail.html',context)



def admin_orders_view(request):
    context = {}

    orders = Order.objects.all()
    packages = Package.objects.all()
    branches = Branch.objects.all()

    if 'branch_name' in request.GET:
        branch_name = request.GET.get('branch_name')
        if branch_name:
            orders = orders.filter(branch_name__name=branch_name)
        context['selected_branch'] = branch_name

    if 'package_name' in request.GET:
        package_name = request.GET.get('package_name')
        if package_name:
            orders = orders.filter(package_name__name=package_name)
        context['selected_package'] = package_name

    context['packages'] = packages
    context['branches'] = branches
    context['orders'] = orders

    return render(request, 'admin_page/admin_orders_view.html', context)


def admin_order_detail(request):
    context={}

    if request.method == "POST":
        order_id=request.POST.get('id')

        context['data']=Order.objects.get(id=order_id)


    return render(request, 'admin_page/admin_order_detail.html',context)







@login_required(login_url='login')
def order(request):
    context = {}
    
    # orders for the currently logged-in user
    user_orders = Order.objects.filter(username=request.user)
    
    # Initialize an empty list to store package information
    packages = []
  
    for order in user_orders:
        package = order.package_name
        
        # Add package information to the list
        packages.append({
            'name': package.name,
            'image': package.image,
            'price': package.price,
            'order_id': order.id,
            # Add any other information you want to display
        })
    
    # Add the packages_info list to the context dictionary
    context['packages'] = packages
    package=Package.objects.all()
    context['package']=package
    
    # Render the template with the context
    return render(request, 'orders.html', context)

def admin_gallery_view(request):
    context={}
    form=Gallery_form()

    if request.method=="POST":
        form=Gallery_form(request.POST,request.FILES)
        if form.is_valid():
            form.save()




    gallery=Gallery.objects.all()
    context['gallery']=gallery
    context['form']=form

    return render(request,'admin_page/admin_gallery_view.html',context)