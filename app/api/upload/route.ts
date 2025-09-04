import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("file") as File

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 })
    }

    const text = await file.text()
    const lines = text.split("\n")
    const headers = lines[0].split(",")

    const leads = lines
      .slice(1)
      .filter((line) => line.trim())
      .map((line) => {
        const values = line.split(",")
        const lead: any = {}
        headers.forEach((header, index) => {
          lead[header.trim()] = values[index]?.trim() || ""
        })
        return lead
      })

    return NextResponse.json({
      success: true,
      leads,
      stats: {
        totalLeads: leads.length,
        emailsSent: leads.length,
        emailsFailed: 0,
      },
    })
  } catch (error) {
    console.error("Upload error:", error)
    return NextResponse.json({ error: "Failed to process file" }, { status: 500 })
  }
}
