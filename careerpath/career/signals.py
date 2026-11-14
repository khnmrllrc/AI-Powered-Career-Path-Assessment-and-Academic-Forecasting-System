# Signal has been disabled as QR codes are now generated on-demand instead of automatically during registration
# Previously:
# @receiver(pre_save, sender=StudentUser)
# def auto_generate_qr_code(sender, instance, **kwargs):
#     """Automatically generate qr_code if not already set"""
#     if not instance.qr_code:
#         instance.qr_code = uuid.uuid4()
