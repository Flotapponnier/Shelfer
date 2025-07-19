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
