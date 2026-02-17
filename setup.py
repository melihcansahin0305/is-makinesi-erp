from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="is_makinesi_erp",
    version="0.0.1",
    description="İş Makinesi Firması için ERPNext Üzerine Kapsamlı ERP Çözümü",
    author="İş Makinesi ERP",
    author_email="info@ismakinesi.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
