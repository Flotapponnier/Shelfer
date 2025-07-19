from typing import Optional, List, Union
from pydantic import BaseModel, Field
from datetime import date

# Scalar types
Text = str
URL = str
Number = float
Integer = int
Boolean = bool
Date = date

# --- Universal Thing model ---
class Thing(BaseModel):
    name: Optional[Text] = None
    description: Optional[Text] = None
    url: Optional[URL] = None
    image: Optional[Union[URL, List[URL]]] = None
    identifier: Optional[Union[Text, URL]] = None
    sameAs: Optional[Union[URL, List[URL]]] = None

# --- Submodels for nested fields ---
class Brand(Thing):
    logo: Optional[URL] = None
    slogan: Optional[Text] = None

class Review(Thing):
    reviewBody: Optional[Text] = None
    reviewRating: Optional['AggregateRating'] = None

class AggregateRating(Thing):
    ratingValue: Optional[Number] = None
    reviewCount: Optional[Integer] = None

class Offer(Thing):
    price: Optional[Number] = None
    priceCurrency: Optional[Text] = None
    availability: Optional[Text] = None
    sku: Optional[Text] = None
    validFrom: Optional[Date] = None
    validThrough: Optional[Date] = None
    url: Optional[URL] = None

class Organization(Thing):
    pass

class Person(Thing):
    pass

class AdditionalProperty(BaseModel):
    propertyID: Optional[Text] = None
    value: Optional[Union[Text, Number, Boolean, URL]] = None
    unitText: Optional[Text] = None
    unitCode: Optional[Text] = None

class IsVariantOf(BaseModel):
    productGroupID: Optional[Text] = None
    variesBy: Optional[List[Text]] = None
    hasVariant: Optional[List['Product']] = None  # Circular, see below

class Model(BaseModel):
    predecessorOf: Optional['Product'] = None
    successorOf: Optional['Product'] = None
    isVariantOf: Optional[IsVariantOf] = None

# --- Main Product model ---
class Product(Thing):
    # Identifiers
    productID: Optional[Text] = None
    sku: Optional[Text] = None
    mpn: Optional[Text] = None
    gtin: Optional[Text] = None
    gtin12: Optional[Text] = None
    gtin13: Optional[Text] = None
    gtin14: Optional[Text] = None
    gtin8: Optional[Text] = None
    asin: Optional[Text] = None

    # Properties
    brand: Optional[Union[Brand, Organization, Text]] = None
    model: Optional[Union[Text, Model]] = None
    color: Optional[Text] = None
    material: Optional[Union[Text, URL]] = None
    weight: Optional[Number] = None
    height: Optional[Number] = None
    width: Optional[Number] = None
    depth: Optional[Number] = None
    size: Optional[Union[Text, Number]] = None
    pattern: Optional[Text] = None
    image: Optional[Union[URL, List[URL]]] = None

    # Relations
    manufacturer: Optional[Union[Organization, Person, Text]] = None
    isAccessoryOrSparePartFor: Optional[List['Product']] = None
    isConsumableFor: Optional[List['Product']] = None
    isRelatedTo: Optional[List['Product']] = None
    isSimilarTo: Optional[List['Product']] = None
    isVariantOf: Optional[IsVariantOf] = None

    # Offer, Review, Rating
    offers: Optional[Union[Offer, List[Offer]]] = None
    review: Optional[Union[Review, List[Review]]] = None
    aggregateRating: Optional[AggregateRating] = None

    # Dates
    releaseDate: Optional[Date] = None
    productionDate: Optional[Date] = None
    purchaseDate: Optional[Date] = None

    # Misc
    additionalProperty: Optional[Union[AdditionalProperty, List[AdditionalProperty]]] = None
    audience: Optional[Text] = None
    category: Optional[Union[Text, URL]] = None
    countryOfOrigin: Optional[Text] = None
    slogan: Optional[Text] = None
    award: Optional[Union[Text, List[Text]]] = None
    keywords: Optional[Union[Text, List[Text]]] = None

# --- ProductGroup model ---
class ProductGroup(Product):
    """
    A ProductGroup represents a group of Products that vary only in certain well-described ways, 
    such as by size, color, material etc.
    
    While a ProductGroup itself is not directly offered for sale, the various varying products 
    that it represents can be. The ProductGroup serves as a prototype or template, standing in 
    for all of the products who have an isVariantOf relationship to it.
    """
    # ProductGroup specific properties
    hasVariant: Optional[List['Product']] = None
    productGroupID: Optional[Text] = None
    variesBy: Optional[Union[Text, List[Text]]] = None

# --- ProductModel model ---
class ProductModel(Product):
    """
    A datasheet or vendor specification of a product (in the sense of a prototypical description).
    
    Use this type when you are describing a product datasheet rather than an actual product,
    e.g. if you are the manufacturer of the product and want to mark up your product 
    specification pages.
    """
    # ProductModel specific properties
    isVariantOf: Optional[Union['ProductGroup', 'ProductModel']] = None
    predecessorOf: Optional['ProductModel'] = None
    successorOf: Optional['ProductModel'] = None

# --- ProductCollection model ---
class ProductCollection(Product):
    """
    A set of products (either ProductGroups or specific variants) that are listed together 
    e.g. in an Offer.
    """
    # ProductCollection specific properties
    includesObject: Optional['TypeAndQuantityNode'] = None
    collectionSize: Optional[Integer] = None

# --- TypeAndQuantityNode model for ProductCollection ---
class TypeAndQuantityNode(BaseModel):
    """
    A node that indicates the exact quantity of products included in an Offer or ProductCollection.
    """
    typeOfGood: Optional[Union['Product', 'ProductGroup', 'ProductModel']] = None
    amountOfThisGood: Optional[Number] = None
    unitCode: Optional[Text] = None
    unitText: Optional[Text] = None
    businessFunction: Optional[Text] = None

# Fix forward references
Product.update_forward_refs()
ProductGroup.update_forward_refs()
ProductModel.update_forward_refs()
ProductCollection.update_forward_refs()
TypeAndQuantityNode.update_forward_refs()
Review.update_forward_refs()
AggregateRating.update_forward_refs()
Model.update_forward_refs()
IsVariantOf.update_forward_refs() 