import random
from time import time
from datetime import datetime

from flask_seeder import Seeder, generator
from flask_seeder.generator import Generator

from betsy.models.merchant import Merchant
from betsy.models.order import Order
from betsy.models.order_item import OrderItem
from betsy.models.product import Product
from betsy.models.product_category import product_category
from betsy.models.category import Category
from betsy.models.review import Review
from betsy.models.order_status import OrderStatus

# All seeders inherit from Seeder
class Adjective(Generator):
    def generate(self):
        words = ["agreeable", "cowardly", "ten", "violet", "grotesque", "tawdry",
            "long-term", "absorbed", "environmental", "alcoholic", "spotless",
            "swanky", "stingy", "spicy", "melted", "proud", "jittery", "repulsive",
            "utter", "stereotyped", "abandoned", "yellow", "roomy", "apathetic",
            "victorious", "magnificent", "windy", "nauseating", "adamant", "cloistered",
            "dead", "bizarre", "voiceless", "ill-informed", "tearful", "worthless",
            "silent", "kindly", "pricey", "kind", "scientific", "near", "pure",
            "warm", "serious", "handsomely", "debonair", "careless", "impressive",
            "cold"]
        return random.choice(words)

class Noun(Generator):
    def generate(self):
        words = ["engineering", "manufacturer", "wife", "energy", "connection", "restaurant",
            "beer", "community", "property", "food", "technology", "mood", "area",
            "foundation", "girlfriend", "preference", "emotion", "poet", "garbage",
            "city", "competition", "steak", "music", "health", "preparation", "reputation",
            "boyfriend", "resolution", "art", "expression", "instruction", "variety",
            "quantity", "cigarette", "intention", "grocery", "performance", "death",
            "presentation", "friendship", "cousin", "extent", "manager", "alcohol",
            "secretary", "confusion", "freedom", "hall", "responsibility", "song"]
        return random.choice(words)

class CreditCardNumber(Generator):
    def __init__(self):
        super().__init__()
        self._number = generator.Integer(start=0, end=9999)

    def generate(self):
        n_0 = self._number.generate()
        n_1 = self._number.generate()
        n_2 = self._number.generate()
        n_3 = self._number.generate()
        return f"{n_0:04d} {n_1:04d} {n_2:04d} {n_3:04d}"

class OrderedDate(Generator):
    def __init__(self):
        super().__init__()
        now = int(time() - 60 * 60 * 24 * 15)
        self._number = generator.Integer(start=now - 60 * 60 * 24 * 365, end=now)

    def generate(self):
        return datetime.fromtimestamp(self._number.generate())

class ShippedDate(Generator):
    def __init__(self):
        super().__init__()
        now = int(time())
        self._number = generator.Integer(start=now - 60 * 60 * 24 * 15, end=now)

    def generate(self):
        return datetime.fromtimestamp(self._number.generate())

class CreditCardCvv(Generator):
    def __init__(self):
        super().__init__()
        self._number = generator.Integer(start=0, end=999)

    def generate(self):
        cvv = self._number.generate()
        return f"{cvv:03d}"

class CreditCardZip(Generator):
    def __init__(self):
        super().__init__()
        self._number = generator.Integer(start=0, end=99999)

    def generate(self):
        zipcode = self._number.generate()
        return f"{zipcode:05d}"

class CreditCardExp(Generator):
    def __init__(self):
        super().__init__()
        self._month = generator.Integer(start=1, end=12)
        self._year = generator.Integer(start=2021, end=2025)

    def generate(self):
        month = self._month.generate()
        year = self._year.generate()
        return f"{month}/{year}"

class StreetAddress(Generator):
    def generate(self):
        # pylint: disable=line-too-long
        addresses = [ "235 Griffin St. Clinton, MD 20735", "60 Linden Ave. Middle River, MD 21220",
            "274 Front St. Hermitage, TN 37076", "277 Briarwood Lane Ankeny, IA 50023",
            "9178 Yukon St. Marquette, MI 49855", "8 Fawn St. Royal Oak, MI 48067",
            "94 Carson Avenue Peoria, IL 61604", "466 Cobblestone Court Central Islip, NY 11722",
            "346 Oakland Lane Lacey, WA 98503", "9178 Sage Street Apt 31 Nutley, NJ 07110",
            "7333 Lookout Ave. Beachwood, OH 44122", "9610 Hillcrest St. Stone Mountain, GA 30083",
            "9991 Branch Court Danville, VA 24540", "529 Berkshire Lane Yonkers, NY 10701",
            "75 Helen Rd. Omaha, NE 68107", "83 Walt Whitman St. New Kensington, PA 15068",
            "559 Catherine Ave. Zionsville, IN 46077", "9959 Warren Dr. Petersburg, VA 23803",
            "9 Snake Hill Avenue Dunedin, FL 34698", "33 Blackburn Ave. Newtown, PA 18940",
            "823 Fairway Ave. Saginaw, MI 48601", "459 S. Jackson St. Ashland, OH 44805",
            "656 Illinois Court Sulphur, LA 70663", "7281 Clark St. Anchorage, AK 99504",
            "457 Jones Avenue Kaukauna, WI 54130", "8062 Fairground Avenue Grove City, OH 43123",
            "8217 West Talbot St. Brentwood, NY 11717", "14 Nicolls Ave. Great Falls, MT 59404",
            "28 La Sierra Road Rosedale, NY 11422", "8286 James Dr. Starkville, MS 39759",
            "409 Galvin Drive Belleville, NJ 07109", "529 Berkshire St. Milwaukee, WI 53204",
            "27 Shadow Brook Street Basking Ridge, NJ 07920", "923 1st Court Holly Springs, NC 27540",
            "20 Lake Road West Lafayette, IN 47906", "8487 Charles St. Bridgeton, NJ 08302",
            "9171 Stillwater Street Huntley, IL 60142", "13 Sierra Street Clearwater, FL 33756",
            "63 North Ave. Dekalb, IL 60115", "688 Walnut Court Manassas, VA 20109",
            "8183 Rockwell Avenue Newnan, GA 30263", "6 University St. North Ridgeville, OH 44039",
            "64 West Washington Ave. Elk Grove Village, IL 60007", "956 Buckingham Ave. Land O Lakes, FL 34639",
            "776 Meadow Ave. Thornton, CO 80241", "8466 New Saddle Road Holyoke, MA 01040",
            "7964 Blackburn St. Brockton, MA 02301", "454 Poor House St. Vienna, VA 22180",
            "53 Miles Lane Middletown, CT 06457", "797 Glen Creek Ave. East Haven, CT 06512",
            "915 E. Vermont Lane Groton, CT 06340", "513 Woodland Drive Faribault, MN 55021",
            "8508 Westport Drive Champlin, MN 55316", "8414 Lees Creek Street Portland, ME 04103",
            "8719 Alton Rd. Ashtabula, OH 44004", "26 Summit Dr. Hyde Park, MA 02136",
            "465 East Avenue Piedmont, SC 29673", "9742 Woodside Lane Pelham, AL 35124",
            "84 White Ave. Greensburg, PA 15601", "9959 County St. Monroeville, PA 15146",
            "8458 St Louis Ave. Beltsville, MD 20705", "7816 Summerhouse Road Paterson, NJ 07501",
            "382 W. Ashley Avenue Kent, OH 44240", "7830 Edgewood Drive Phillipsburg, NJ 08865",
            "17 Shady Ave. Pembroke Pines, FL 33028", "12 Brewery St. Independence, KY 41051",
            "7 Surrey Rd. Lenoir, NC 28645", "279 Church Dr. Taylors, SC 29687",
            "7770 Oakland St. Grandville, MI 49418", "86 Cross Street Newark, NJ 07103",
            "980 Pennsylvania Court Reston, VA 20191", "810 Marshall Street Redondo Beach, CA 90278",
            "30 Bald Hill Court North Bergen, NJ 07047", "7253 Hill Field Road Westmont, IL 60559",
            "688 Beach Street Stillwater, MN 55082", "4 Bridle St. Bismarck, ND 58501",
            "11 Lake Forest St. San Antonio, TX 78213", "75 Golden Star Lane Cranford, NJ 07016",
            "436 Tarkiln Hill Ave. Niles, MI 49120", "8080 SE. Fairground St. Garland, TX 75043",
            "2 Front St. Hastings, MN 55033", "7458 Division Drive Mcdonough, GA 30252",
            "714 South Henry Smith Road Clifton, NJ 07011", "793 Pacific Dr. Nazareth, PA 18064",
            "7920 Garfield Dr. West Fargo, ND 58078", "970 Spruce Lane Sewell, NJ 08080",
            "53 Tanglewood Rd. Canal Winchester, OH 43110", "316 Miles Rd. Butte, MT 59701",
            "94 N. Fordham Street Bowling Green, KY 42101", "631 Squaw Creek St. Mount Prospect, IL 60056",
            "60C SW. Rockville Street Deerfield Beach, FL 33442", "97 Locust St. Wyandotte, MI 48192",
            "327 N. Pleasant Ave. North Augusta, SC 29841", "87 Mayflower Court Powder Springs, GA 30127",
            "267 Hilldale St. Warwick, RI 02886", "78 Richardson Ave. Arvada, CO 80003",
            "31 Pendergast Circle Mundelein, IL 60060", "31 Winchester Lane Trumbull, CT 06611",
            "982 Lake Ave. Matawan, NJ 07747", "578 Mammoth Ave. Sugar Land, TX 77478"
        ]
        return random.choice(addresses)

class Sentence(Generator):
    def generate(self):
        # pylint: disable=line-too-long
        sentences = [
            "The knives were out and she was sharpening hers.",
            "It's a skateboarding penguin with a sunhat!",
            "Chocolate covered crickets were his favorite snack.",
            "It doesn't sound like that will ever be on my travel list.",
            "The crowd yells and screams for more memes.",
            "They say that dogs are man's best friend, but this cat was setting out to sabotage that theory.",
            "The old apple revels in its authority.",
            "Joe made the sugar cookies; Susan decorated them.",
            "I met an interesting turtle while the song on the radio blasted away.",
            "I am counting my calories, yet I really want dessert.",
            "It was the best sandcastle he had ever seen.",
            "He wondered if it could be called a beach if there was no sand.",
            "A dead duck doesn't fly backward.",
            "One small action would change her life, but whether it would be for better or for worse was yet to be determined.",
            "The sunblock was handed to the girl before practice, but the burned skin was proof she did not apply it.",
            "The near-death experience brought new ideas to light.",
            "I just wanted to tell you I could see the love you have for your child by the way you look at her.",
            "It was her first experience training a rainbow unicorn.",
            "He uses onomatopoeia as a weapon of mental destruction.",
            "She always had an interesting perspective on why the world must be flat.",
            "The fog was so dense even a laser decided it wasn't worth the effort.",
            "He found a leprechaun in his walnut shell.",
            "The gruff old man sat in the back of the bait shop grumbling to himself as he scooped out a handful of worms.",
            "A purple pig and a green donkey flew a kite in the middle of the night and ended up sunburnt.",
            "She wrote him a long letter, but he didn't read it.",
            "He turned in the research paper on Friday; otherwise, he would have not passed the class.",
            "Erin accidentally created a new universe.",
            "He excelled at firing people nicely.",
            "Andy loved to sleep on a bed of nails.",
            "Behind the window was a reflection that only instilled fear.",
            "He dreamed of eating green apples with worms.",
            "He loved eating his bananas in hot dog buns.",
            "We have young kids who often walk into our room at night for various reasons including clowns in the closet.",
            "Sometimes it is better to just walk away from things and go back to them later when you’re in a better frame of mind.",
            "Be careful with that butter knife.",
            "He had reached the point where he was paranoid about being paranoid.",
            "This book is sure to liquefy your brain.",
            "She had a habit of taking showers in lemonade.",
            "The clouds formed beautiful animals in the sky that eventually created a tornado to wreak havoc.",
            "He told us a very exciting adventure story.",
            "Flesh-colored yoga pants were far worse than even he feared.",
            "When motorists sped in and out of traffic, all she could think of was those in need of a transplant.",
            "Stop waiting for exceptional things to just happen.",
            "While on the first date he accidentally hit his head on the beam.",
            "When nobody is around, the trees gossip about the people who have walked under them.",
            "The newly planted trees were held up by wooden frames in hopes they could survive the next storm.",
            "He appeared to be confusingly perplexed.",
            "That was how he came to win $1 million.",
            "The fact that there's a stairway to heaven and a highway to hell explains life well.",
            "Karen realized the only way she was getting into heaven was to cheat."
        ]
        return random.choice(sentences)

class Picsum(Generator):
    def generate(self):
        dims = [
            [200, 300],
            [200, 200],
            [300, 300],
            [300, 200],
        ]
        dim = random.choice(dims)
        return f"https://picsum.photos/{dim[0]}/{dim[1]}"

class ProductName(Generator):
    def __init__(self):
        super().__init__()
        self._adj = Adjective()
        self._noun = Noun()

    def generate(self):
        return f"{self._adj.generate()} {self._noun.generate()}"

class StandardSeeder(Seeder):

    def fix_orders(self, order):
        if order.status != OrderStatus.PAID.value:
            return

        for item in order.order_items:
            if not item.shipped_date:
                return

        order.status = OrderStatus.COMPLETED.value

    # run() will be called by Flask-Seeder
    def run(self):
        # Create a new Faker and tell it how to create User objects
        name_gen = generator.Name()
        noun_gen = Noun()
        prod_name_gen = ProductName()
        sentence_gen = Sentence()
        price_gen = generator.Integer(start=100, end=5000)
        picsum_gen = Picsum()
        stock_gen = generator.Integer(start=0, end=25)
        bool_gen = generator.Integer(start=0, end=1)
        addr_gen = StreetAddress()
        cc_number = CreditCardNumber()
        cc_exp = CreditCardExp()
        cc_cvv = CreditCardCvv()
        cc_zip = CreditCardZip()
        ordered_date = OrderedDate()
        shipped_date = ShippedDate()

        # faker = Faker(
        #     cls=Merchant,
        #     init={
        #         "name": generator.Name(),
        #         "email": generator.String(r'\c{3,8}.\c{3,8}@\c{3,8}.com')
        #     }
        # )

        self.db.session.connection().execute(product_category.delete())  # pylint: disable=no-member
        self.db.session.commit()

        OrderItem.query.delete()
        Order.query.delete()
        Review.query.delete()
        Category.query.delete()
        Product.query.delete()
        Merchant.query.delete()
        self.db.session.commit()

        # Create users
        merchants = []
        for uid in range(10):
            name = name_gen.generate()
            email = f"{name.lower()}@mail.com"
            provider = "sample"
            merchant = Merchant(name=name, email=email, provider=provider, uid=uid)
            merchants.append(merchant)

            print(f"Adding user: {merchant}")
            self.db.session.add(merchant)

        self.db.session.commit()

        # Create categories
        categories = []
        for _ in range(10):
            name = noun_gen.generate()
            category = Category(name=name)
            categories.append(category)

            print(f"Adding category: {category}")
            self.db.session.add(category)

        self.db.session.commit()

        products = []
        for _ in range(50):
            name = prod_name_gen.generate()
            description = sentence_gen.generate()
            price = price_gen.generate()
            photo_url = picsum_gen.generate()
            stock = stock_gen.generate()
            discontinued = bool(bool_gen.generate())
            merchant_id = random.choice(merchants).id
            product = Product(name=name, description=description, price=price,
                photo_url=photo_url, stock=stock, discontinued=discontinued,
                merchant_id = merchant_id)
            products.append(product)

            category_count = random.randint(0, 3)
            product_categories = random.sample(categories, category_count)
            for category in product_categories:
                product.categories.append(category)

            print(f"Adding product: {product}")
            self.db.session.add(product)

        for product in random.sample(products, random.randint(30, 50)):
            review_count = random.randint(1, 5)
            for _ in range(review_count):
                rating = random.randint(1, 5)
                comment = sentence_gen.generate()
                review = Review(rating=rating, comment=comment, product=product)

                self.db.session.add(review)

        self.db.session.commit()

        orders = []
        for merchant in merchants:
            order_count = random.randint(0, 20)
            statuses = OrderStatus.all()
            for _ in range(order_count):
                status = random.sample(statuses, 1)[0]
                order = Order()
                orders.append(order)
                name = name_gen.generate()
                email = f"{name.lower()}@mail.com"
                order.email = email
                order.mailing_address = addr_gen.generate()
                order.cc_name = name
                order.cc_number = cc_number.generate()
                order.cc_exp = cc_exp.generate()
                order.cc_cvv = cc_cvv.generate()
                order.cc_zipcode = cc_zip.generate()
                order.status = status
                if status != OrderStatus.PENDING.value:
                    order.ordered_date = ordered_date.generate()

                self.db.session.add(order)
                self.db.session.commit()

                item_count = random.randint(1, 5)
                order_products = random.sample(products, item_count)
                for product in order_products:
                    quantity = random.randint(1, 5)
                    item = OrderItem()
                    item.product = product
                    item.order = order
                    item.purchase_price = product.price
                    item.quantity = quantity
                    if order.status == OrderStatus.PAID.value:
                        item.shipped_date = random.sample([None, shipped_date.generate()], 1)[0]
                    elif order.status == OrderStatus.COMPLETED.value:
                        item.shipped_date = shipped_date.generate()

                    self.db.session.add(item)

                self.db.session.commit()

                # update order status
                for order in orders:
                    self.fix_orders(order)

                self.db.session.commit()
