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
import { Download } from "lucide-react";
import { RefreshCw } from "lucide-react";

export default function ProductDataEnrichment({ data }: { data: Product }) {
	const { enrichedProduct, updateFieldValue, diffResult, setEnrichedProduct } = useProductData(
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

	// Remove field handler
	const handleRemoveField = (fieldPath: string) => {
		const pathArray = fieldPath.split(".");
		// Always deep clone to avoid mutating the original object
		const newData = JSON.parse(JSON.stringify(enrichedProduct));
		let current: Record<string, unknown> = newData;
		for (let i = 0; i < pathArray.length - 1; i++) {
			if (!current[pathArray[i]]) return; // Path does not exist
			current = current[pathArray[i]] as Record<string, unknown>;
		}
		const finalKey = pathArray[pathArray.length - 1];
		if (Array.isArray(current)) {
			const idx = parseInt(finalKey.replace(/\[|\]/g, ""), 10);
			if (!isNaN(idx)) (current as unknown as unknown[]).splice(idx, 1);
		} else {
			delete current[finalKey];
		}
		// Always set a new object at the root to avoid mutating the original
		setEnrichedProduct(newData);
	};

	return (
		<div className="min-h-screen">
			<div className="mx-auto w-full">
				{/* Main Heading */}
				<div className="text-center mb-8">
					<p className="text-lg text-gray-600">
						Approve and edit the enriched product data here
					</p>
				</div>

				{/* Single Panel Layout - Only Enriched Product Data */}
				<div className="w-full px-2 sm:px-4 md:px-8 lg:px-16 xl:px-32 2xl:px-64">
					<Card className="h-fit">
						<CardHeader className="pb-4 flex flex-row items-center justify-between">
							<CardTitle className="text-xl font-semibold text-gray-800 flex items-center gap-2">
								<div className="w-3 h-3 bg-green-500 rounded-full"></div>
								Enriched Product Data
								<span className="text-sm font-normal text-gray-500 ml-2">
									(Click values to edit • Hover to approve/decline)
								</span>
							</CardTitle>
							<button
								onClick={() => {
									resetValidation();
									setEnrichedProduct(JSON.parse(JSON.stringify(initialEnrichedProduct)));
								}}
								className="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 bg-gray-200 text-gray-700 hover:bg-gray-300 hover:shadow-lg transform hover:scale-105"
							>
								<RefreshCw className="w-4 h-4" />
								Reset Validation
							</button>
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
									onRemoveField={handleRemoveField}
								/>
							</div>
						</CardContent>
					</Card>
				</div>

				{/* Action Buttons */}
				<div className="flex justify-center gap-4 mt-8">
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
