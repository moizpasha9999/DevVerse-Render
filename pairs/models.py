from django.db import models

# Create your models here.
from django.db import models

class Member(models.Model):
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email_id = models.EmailField(unique=True)
    roll_no = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.full_name} ({self.roll_no})"


class Pair(models.Model):
    member_1 = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='pair_member_1')
    member_2 = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='pair_member_2')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Pair: {self.member_1.full_name} & {self.member_2.full_name}"


class Request(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    sent_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='sent_requests')
    sent_to = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sent_by.roll_no} -> {self.sent_to.roll_no} ({self.status})"