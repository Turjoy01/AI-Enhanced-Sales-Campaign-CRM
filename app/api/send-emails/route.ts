import { type NextRequest, NextResponse } from "next/server"

interface Lead {
  LeadID: string
  "First Name": string
  "Last Name": string
  Email: string
  Phone: string
  "Interest Category": string
  "Lead Score": number
  "Buyer Persona": string
  "Generated Email"?: string
  "Email Status"?: string
}

interface EmailCredentials {
  email: string
  appPassword: string
}

export async function POST(request: NextRequest) {
  try {
    const { leads, emailCredentials }: { leads: Lead[]; emailCredentials: EmailCredentials } = await request.json()

    if (!leads || !emailCredentials.email || !emailCredentials.appPassword) {
      return NextResponse.json({ success: false, error: "Missing required data" }, { status: 400 })
    }

    let emailsSent = 0
    let emailsFailed = 0
    const updatedLeads = [...leads]

    for (let i = 0; i < updatedLeads.length; i++) {
      const lead = updatedLeads[i]

      try {
        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!lead.Email || !emailRegex.test(lead.Email)) {
          throw new Error("Invalid email format")
        }

        const subject = `Hello ${lead["First Name"]}, We have an offer for you!`

        // Use generated email if available, otherwise create a simple message
        const body =
          lead["Generated Email"] ||
          `Dear ${lead["First Name"]} ${lead["Last Name"]},

We hope this email finds you well. We have exciting opportunities in ${lead["Interest Category"]} that might interest you.

Based on your profile as a ${lead["Buyer Persona"]}, we believe our solutions could be a great fit for your needs.

We'd love to discuss how we can help you achieve your goals.

Best regards,
Sales Team`

        const simulateEmailSending = () => {
          // 90% success rate simulation
          const random = Math.random()
          if (random < 0.9) {
            return { success: true }
          } else {
            return { success: false, error: "Temporary server error" }
          }
        }

        const result = simulateEmailSending()

        if (result.success) {
          updatedLeads[i]["Email Status"] = "Sent"
          emailsSent++
          } else {
          throw new Error(result.error || "Failed to send email")
        }

        // Add delay to simulate real email sending
        await new Promise((resolve) => setTimeout(resolve, 500))
      } catch (error) {
        console.error(`Failed to send email to ${lead.Email}:`, error)
        updatedLeads[i]["Email Status"] = `Failed: ${error instanceof Error ? error.message : "Unknown error"}`
        emailsFailed++
      }
    }

    return NextResponse.json({
      success: true,
      updatedLeads,
      emailsSent,
      emailsFailed,
    })
  } catch (error) {
    console.error("Error in send-emails API:", error)
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}
