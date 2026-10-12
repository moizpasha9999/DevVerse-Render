from django.db import transaction
from .models import Member

STUDENTS_DATA = [
    {
        "roll_no": "BSEF26M501",
        "full_name": "Moiz Pasha",
        "phone": "+923286970772",
        "email_id": "bsef26m501@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M502",
        "full_name": "Anza Sultan",
        "phone": "+923200798597",
        "email_id": "bsef26m502@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M503",
        "full_name": "Anmol Arshad",
        "phone": "+923294290815",
        "email_id": "bsef26m503@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M504",
        "full_name": "Mumtahina Rafiq",
        "phone": "+923295545655",
        "email_id": "bsef26m504@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M505",
        "full_name": "Noman Rasool",
        "phone": "+923060016289",
        "email_id": "bsef26m505@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M506",
        "full_name": "Mahnoor",
        "phone": "+923214590616",
        "email_id": "bsef26m506@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M507",
        "full_name": "Muntaha Ijaz",
        "phone": "+923491331825",
        "email_id": "bsef26m507@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M508",
        "full_name": "Muhammad Salman",
        "phone": "+923178272987",  # Note: 2 Muhammad Salmans exist
        "email_id": "bsef26m508@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M509",
        "full_name": "Aiman Ali",
        "phone": "+923014256109",
        "email_id": "bsef26m509@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M510",
        "full_name": "Muhammad Umar Baig",
        "phone": "+923064455526",
        "email_id": "bsef26m510@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M511",
        "full_name": "Abdul Hanan Khan",
        "phone": "+923216039579",
        "email_id": "bsef26m511@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M512",
        "full_name": "Faiza Akram",
        "phone": "+923264851624",
        "email_id": "bsef26m512@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M513",
        "full_name": "Maryam Jabbar",
        "phone": "+923153023102",
        "email_id": "bsef26m513@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M514",
        "full_name": "Ahmad Raza",
        "phone": "+923174357298",
        "email_id": "bsef26m514@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M515",
        "full_name": "Adan Fatima Khan",
        "phone": "+923032826719",
        "email_id": "bsef26m515@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M516",
        "full_name": "Hafiz Taha Tariq",
        "phone": "+923467754510",
        "email_id": "bsef26m516@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M517",
        "full_name": "Muhammad Mateen Adil",
        "phone": "+923003610136",  # MISSING
        "email_id": "bsef26m517@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M518",
        "full_name": "Muhammad Salman",
        "phone": "+923207874708",  
        "email_id": "bsef26m518@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M519",
        "full_name": "Farzam Haider",
        "phone": "+923458738571",
        "email_id": "bsef26m519@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M520",
        "full_name": "Zainab Binte Tariq",
        "phone": "+923326280356",
        "email_id": "bsef26m520@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M521",
        "full_name": "Khadija Amir",
        "phone": "+923144027320",  # MISSING
        "email_id": "bsef26m521@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M522",
        "full_name": "Faheem Ahmed",
        "phone": "+923290166363",
        "email_id": "bsef26m522@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M523",
        "full_name": "Meerab Asghar",
        "phone": None,  # MISSING
        "email_id": "bsef26m523@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M524",
        "full_name": "Manal Chaudhry",
        "phone": "+923290225506",
        "email_id": "bsef26m524@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M525",
        "full_name": "Arsla Malik",
        "phone": "+923266154802",
        "email_id": "bsef26m525@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M526",
        "full_name": "Aswad Abdullah",
        "phone": "+923288156468",
        "email_id": "bsef26m526@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M527",
        "full_name": "Muhammad Anas",
        "phone": "+923218471449",
        "email_id": "bsef26m527@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M528",
        "full_name": "Hussain Jamil",
        "phone": "+923096089702",
        "email_id": "bsef26m528@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M529",
        "full_name": "Laiba",
        "phone": "+923281052883",  # MISSING
        "email_id": "bsef26m529@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M530",
        "full_name": "Muhammad Abu Zar Ghumman",
        "phone": "+923075063342",
        "email_id": "bsef26m530@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M531",
        "full_name": "Zaeem Hussain",
        "phone": "+923094956901",  # MISSING
        "email_id": "bsef26m531@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M532",
        "full_name": "Saif Ullah Asghar",
        "phone": "+923262657311",
        "email_id": "bsef26m532@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M533",
        "full_name": "Ghulam Yaseen",
        "phone": "+923154795862",
        "email_id": "bsef26m533@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M534",
        "full_name": "Fatima Nauman",
        "phone": "+923079648822",
        "email_id": "bsef26m534@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M535",
        "full_name": "Muhammad Taha",
        "phone": "+923704088720",
        "email_id": "bsef26m535@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M536",
        "full_name": "Muhammad Saim Asif",
        "phone": "+923343184344",
        "email_id": "bsef26m536@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M537",
        "full_name": "Noor Amna",
        "phone": "+923192277932",
        "email_id": "bsef26m537@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M538",
        "full_name": "Tabinda Bilal",
        "phone": "+923414421613",
        "email_id": "bsef26m538@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M539",
        "full_name": "Muhammad Awais",
        "phone": "+923060733373",
        "email_id": "bsef26m539@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M540",
        "full_name": "Abdullah Shahbaz",
        "phone": "+923104017879",
        "email_id": "bsef26m540@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M541",
        "full_name": "Bisma Rafique",
        "phone": "+923258759860",
        "email_id": "bsef26m541@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M542",
        "full_name": "Rija Pasha",
        "phone": "+923481720064",
        "email_id": "bsef26m542@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M543",
        "full_name": "Muhammad Rehan Shahzad",
        "phone": "+923244845093",
        "email_id": "bsef26m543@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M544",
        "full_name": "Muhammad Saad Azhar",
        "phone": "+923215501926",
        "email_id": "bsef26m544@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M545",
        "full_name": "Zainab Fatima Ali",
        "phone": "+923214123133",
        "email_id": "bsef26m545@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M546",
        "full_name": "Syed Mamnoon Haider Shah",
        "phone": "+923284203148",
        "email_id": "bsef26m546@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M547",
        "full_name": "Sheeza Shoukat",
        "phone": "+923047303213",
        "email_id": "bsef26m547@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M548",
        "full_name": "Muhammad Asad",
        "phone": "+923267995407",
        "email_id": "bsef26m548@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M549",
        "full_name": "Syeda Laiba Nadir",
        "phone": "+923281052883",
        "email_id": "bsef26m549@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M550",
        "full_name": "Muhammad Zain",
        "phone": "+923000966953",
        "email_id": "bsef26m550@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M551",
        "full_name": "Moiz Haider",
        "phone": "+923074042971",
        "email_id": "bsef26m551@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M552",
        "full_name": "Naeem Ullah Ghafoor",
        "phone": "+923234281861",  # MISSING
        "email_id": "bsef26m552@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M553",
        "full_name": "Mehak Sajjad",
        "phone": "+923135560175",
        "email_id": "bsef26m553@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M554",
        "full_name": "Iqra Qasim",
        "phone": "+923284750384",
        "email_id": "bsef26m554@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M555",
        "full_name": "Abdullah Bin Zahid",
        "phone": "+923025989744",
        "email_id": "bsef26m555@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M556",
        "full_name": "Eman Shafiq",
        "phone": "+923254914607",
        "email_id": "bsef26m556@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M557",
        "full_name": "Hammad Zubair",
        "phone": None,  # MISSING
        "email_id": "bsef26m557@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M558",
        "full_name": "Shazmah Zahra",
        "phone": "+923337893685",  # MISSING
        "email_id": "bsef26m558@pucit.edu.pk",
    },
    {
        "roll_no": "BSEF26M559",
        "full_name": "Danyal Ahmad",
        "phone": None,  # MISSING
        "email_id": "bsef26m559@pucit.edu.pk",
    },
]

def populate_members(data=None, default_phone="N/A"):
    """
    Populates or updates the Member table with student records.
    
    :param data: List of student dicts (defaults to STUDENTS_DATA)
    :param default_phone: Fallback value for students with missing phone numbers
    :return: Tuple containing (created_count, updated_count)
    """
    if data is None:
        data = STUDENTS_DATA

    created_count = 0
    updated_count = 0

    # Wrap in atomic transaction so either all succeed or none do
    with transaction.atomic():
        for item in data:
            # Fallback if phone is missing or None
            phone_number = item.get("phone") or default_phone

            member, created = Member.objects.update_or_create(
                roll_no=item["roll_no"],
                defaults={
                    "full_name": item["full_name"],
                    "email_id": item["email_id"],
                    "phone": phone_number,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

    print(f"Done! Created: {created_count}, Updated: {updated_count}")
    return created_count, updated_count