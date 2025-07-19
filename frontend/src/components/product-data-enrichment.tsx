"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import JsonTreeView from "./json-tree-view";
import {
	originalProduct,
	enrichedProduct as initialEnrichedProduct,
} from "../../data/sample-products";
import { useValidation } from "../hooks/use-validation";
import { useEditing } from "../hooks/use-editing";
import { useProductData } from "../hooks/use-product-data";
import DownloadButton from "../components/download-button";
import {
	generateFinalJson,
	getAllPendingFields,
} from "../../utils/json-generator";
import { downloadJsonFile } from "../../utils/file-download";
import type { JsonValue } from "../../types/json";
import { Product } from "schema-dts";

export default function ProductDataEnrichment({ data }: { data: Product }) {
	const { enrichedProduct, updateFieldValue, diffResult } = useProductData(
		originalProduct,
		initialEnrichedProduct,
	);
	const { validationStates, handleValidation, resetValidation } =
		useValidation();
	const { editingState, startEditing, stopEditing, isEditing } = useEditing();

	const pendingFields = getAllPendingFields(diffResult, validationStates);
	const isDownloadEnabled = pendingFields.length === 0;

	const handleDownload = () => {
		if (!isDownloadEnabled) return;

		const finalJson = generateFinalJson(
			originalProduct,
			enrichedProduct,
			diffResult,
			validationStates,
		);
		downloadJsonFile(finalJson, "enriched_product.json");
	};

	const handleUpdateValue = (fieldPath: string, newValue: JsonValue) => {
		updateFieldValue(fieldPath, newValue);
		// Reset validation state for this field since it's been edited
		if (validationStates[fieldPath]) {
			// You might want to reset the validation state here
			// For now, we'll let the diff system handle it
		}
	};

	return (
		<div className="min-h-screen bg-gray-50 p-6">
			<div className="max-w-7xl mx-auto">
				{/* Main Heading */}
				<div className="text-center mb-8">
					<h1 className="text-4xl font-bold text-gray-900 mb-2">
						Product Data Enrichment
					</h1>
					<p className="text-lg text-gray-600">
						Transform your product data with AI-powered enrichment
					</p>
				</div>

				{/* Two Panel Layout */}
				<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
					{/* Left Panel - Original Product Data */}
					<Card className="h-fit">
						<CardHeader className="pb-4">
							<CardTitle className="text-xl font-semibold text-gray-800 flex items-center gap-2">
								<div className="w-3 h-3 bg-blue-500 rounded-full"></div>
								Original Product Data
							</CardTitle>
						</CardHeader>
						<CardContent>
							<div className="bg-gray-100 rounded-lg p-6 border-2 border-dashed border-gray-300">
								<JsonTreeView data={originalProduct} />
							</div>
						</CardContent>
					</Card>

					{/* Right Panel - Enriched Product Data */}
					<Card className="h-fit">
						<CardHeader className="pb-4">
							<CardTitle className="text-xl font-semibold text-gray-800 flex items-center gap-2">
								<div className="w-3 h-3 bg-green-500 rounded-full"></div>
								Enriched Product Data
								<span className="text-sm font-normal text-gray-500 ml-2">
									(Click values to edit • Hover to approve/decline)
								</span>
							</CardTitle>
						</CardHeader>
						<CardContent>
							<div className="bg-gray-100 rounded-lg p-6 border-2 border-dashed border-gray-300">
								<JsonTreeView
									data={enrichedProduct}
									diffResult={diffResult}
									validationStates={validationStates}
									onValidation={handleValidation}
									editingFieldPath={editingState.fieldPath}
									onStartEditing={startEditing}
									onStopEditing={stopEditing}
									onUpdateValue={handleUpdateValue}
								/>
							</div>
						</CardContent>
					</Card>
				</div>

				{/* Action Buttons */}
				<div className="flex justify-center gap-4 mt-8">
					<button className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
						Upload Data
					</button>
					<button className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors">
						Start Enrichment
					</button>
					<button
						onClick={resetValidation}
						className="px-6 py-3 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors"
					>
						Reset Validation
					</button>
				</div>

				{/* Download Section */}
				<div className="flex justify-center mt-6">
					<DownloadButton
						isEnabled={isDownloadEnabled}
						pendingCount={pendingFields.length}
						onDownload={handleDownload}
					/>
				</div>
			</div>
		</div>
	);
}
