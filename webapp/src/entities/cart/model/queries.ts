import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { cartApi } from "../api/cartApi";
import type { CartResponse } from "./types";
import type { ProductListItem } from "@/entities/product";

export const cartKeys = {
  all: ["cart"] as const,
};

export function useCartQuery() {
  return useQuery({
    queryKey: cartKeys.all,
    queryFn: cartApi.getCart,
    staleTime: 60_000,
  });
}

export function useAddToCartMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ productId, quantity }: { productId: number; quantity: number; product?: ProductListItem }) =>
      cartApi.addItem(productId, quantity),
      
    onMutate: async ({ productId, quantity, product }) => {
      await queryClient.cancelQueries({ queryKey: cartKeys.all });
      const previousCart = queryClient.getQueryData<CartResponse>(cartKeys.all);

      if (previousCart && product) {
        const newItems = [...previousCart.items];
        const existingIndex = newItems.findIndex(i => i.product.id === productId);
        
        if (existingIndex > -1) {
          const item = newItems[existingIndex];
          newItems[existingIndex] = {
            ...item,
            quantity: quantity,
            subtotal: (parseFloat(item.product.price) * quantity).toFixed(2),
          };
        } else {
          newItems.push({
            id: -productId, // temporary negative ID
            product,
            product_id: productId,
            quantity,
            subtotal: (parseFloat(product.price) * quantity).toFixed(2),
          });
        }
        
        const newTotal = newItems.reduce((sum, item) => sum + parseFloat(item.subtotal), 0).toFixed(2);
        
        queryClient.setQueryData<CartResponse>(cartKeys.all, {
          items: newItems,
          total: newTotal
        });
      }
      return { previousCart };
    },
    onError: (err, variables, context) => {
      if (context?.previousCart) {
        queryClient.setQueryData(cartKeys.all, context.previousCart);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
}

export function useRemoveFromCartMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId: number) => cartApi.removeItem(itemId),
    onMutate: async (itemId) => {
      await queryClient.cancelQueries({ queryKey: cartKeys.all });
      const previousCart = queryClient.getQueryData<CartResponse>(cartKeys.all);

      if (previousCart) {
        const newItems = previousCart.items.filter(i => i.id !== itemId);
        const newTotal = newItems.reduce((sum, item) => sum + parseFloat(item.subtotal), 0).toFixed(2);
        
        queryClient.setQueryData<CartResponse>(cartKeys.all, {
          items: newItems,
          total: newTotal
        });
      }
      return { previousCart };
    },
    onError: (err, variables, context) => {
      if (context?.previousCart) {
        queryClient.setQueryData(cartKeys.all, context.previousCart);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
}

export function useClearCartMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => cartApi.clearCart(),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: cartKeys.all });
      const previousCart = queryClient.getQueryData<CartResponse>(cartKeys.all);

      queryClient.setQueryData<CartResponse>(cartKeys.all, {
        items: [],
        total: "0.00"
      });
      return { previousCart };
    },
    onError: (err, variables, context) => {
      if (context?.previousCart) {
        queryClient.setQueryData(cartKeys.all, context.previousCart);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
}
