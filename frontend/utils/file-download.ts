export function downloadJsonFile(data: any, filename = "enriched_product.json"): void {
  try {
    // Convert the data to a formatted JSON string
    const jsonString = JSON.stringify(data, null, 2)

    // Create a Blob with the JSON data
    const blob = new Blob([jsonString], { type: "application/json" })

    // Create a temporary URL for the blob
    const url = URL.createObjectURL(blob)

    // Create a temporary anchor element and trigger the download
    const link = document.createElement("a")
    link.href = url
    link.download = filename
    link.style.display = "none"

    // Append to body, click, and remove
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    // Clean up the temporary URL
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error("Error downloading JSON file:", error)
    alert("Failed to download the file. Please try again.")
  }
}
