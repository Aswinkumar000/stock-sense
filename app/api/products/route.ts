import { NextResponse } from "next/server";
import { z } from "zod";
import prisma from "@/lib/prisma";

const productSchema = z.object({
  name: z.string().min(1, "Product name is required"),
  sku: z.string().min(1, "SKU is required"),
  category: z.string().min(1, "Category is required"),
  uom: z.string().min(1, "Unit of measure is required"),
  initialStock: z.number().min(0, "Initial stock cannot be negative"),
  description: z.string().optional(),
});

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const result = productSchema.safeParse(body);

    if (!result.success) {
      return NextResponse.json(
        { error: result.error.issues[0].message },
        { status: 400 }
      );
    }

    const {
      name,
      sku,
      category,
      uom,
      initialStock,
      description,
    } = result.data;

    const existingProduct = await prisma.product.findUnique({
      where: { sku },
    });

    if (existingProduct) {
      return NextResponse.json(
        { error: "SKU already exists" },
        { status: 409 }
      );
    }

    const productCategory = await prisma.category.upsert({
      where: { name: category },
      update: {},
      create: { name: category },
    });

    const product = await prisma.product.create({
      data: {
        name,
        sku,
        categoryId: productCategory.id,
        uom,
        initialStock,
        description,
      },
      include: {
        category: true,
      },
    });

    return NextResponse.json(
      {
        message: "Product created successfully",
        product,
      },
      { status: 201 }
    );
  } catch (error) {
    console.error("Product creation error:", error);

    return NextResponse.json(
      { error: "Something went wrong" },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const products = await prisma.product.findMany({
      include: {
        category: true,
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    return NextResponse.json(products);
  } catch (error) {
    console.error("Product fetch error:", error);

    return NextResponse.json(
      { error: "Failed to fetch products" },
      { status: 500 }
    );
  }
}