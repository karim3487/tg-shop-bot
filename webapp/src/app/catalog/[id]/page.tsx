import { ProductPage } from "@/views/product";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function ProductRoutePage({ params }: Props) {
  const { id } = await params;
  return <ProductPage productId={Number(id)} />;
}
