from cowin import CoWinAPI

pin_code = "642122"

cowin = CoWinAPI()
available_centers = cowin.get_availability_by_pincode(pin_code)
print(available_centers)