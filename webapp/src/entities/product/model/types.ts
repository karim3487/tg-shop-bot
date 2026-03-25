export interface CategoryChild {
  id: number;
  name: string;
}

export interface Category {
  id: number;
  name: string;
  parent: number | null;
  children: CategoryChild[];
}

export interface ProductImage {
  id: number;
  url: string;
  order: number;
}

export interface ProductListItem {
  id: number;
  name: string;
  price: string; // Django DecimalField → string
  category: number;
  category_name: string;
  thumbnail: ProductImage | null; // Django returns the full ProductImageSerializer object
}

export interface ProductDetail {
  id: number;
  name: string;
  description: string;
  price: string;
  category: Category;
  images: ProductImage[];
  created_at: string;
}

export interface ProductFilters {
  search?: string;
  category?: number;
}
