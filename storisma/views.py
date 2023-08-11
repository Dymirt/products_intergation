from django.http import HttpResponseRedirect
from django.shortcuts import render
from dotenv import load_dotenv
from . import storisma
import os


# Create your views here.
from django.urls import reverse

load_dotenv()


STORISMA_EMAIL = os.getenv("STORISMA_EMAIL")
STORISMA_PASSWORD = os.getenv("STORISMA_PASSWORD")
STORISMA = storisma.Storisma(STORISMA_EMAIL, STORISMA_PASSWORD)
#response = STORISMA.login()


def storisma(request):
    return HttpResponseRedirect(reverse("products:products"))
