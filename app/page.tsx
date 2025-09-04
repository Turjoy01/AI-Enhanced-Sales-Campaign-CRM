"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Upload, Users, Mail, CheckCircle, XCircle, Send } from "lucide-react"

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

interface CampaignStats {
  totalLeads: number
  emailsSent: number
  emailsFailed: number
}

export default function CRMDashboard() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [campaignStats, setCampaignStats] = useState<CampaignStats>({
    totalLeads: 0,
    emailsSent: 0,
    emailsFailed: 0,
  })
  const [isUploading, setIsUploading] = useState(false)
  const [emailCredentials, setEmailCredentials] = useState({
    email: "",
    appPassword: "",
  })
  const [isSendingEmails, setIsSendingEmails] = useState(false)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsUploading(true)

    try {
      const text = await file.text()
      const lines = text.split("\n")
      const headers = lines[0].split(",")

      const parsedLeads: Lead[] = lines
        .slice(1)
        .filter((line) => line.trim())
        .map((line) => {
          const values = line.split(",")
          const lead: any = {}
          headers.forEach((header, index) => {
            lead[header.trim()] = values[index]?.trim() || ""
          })
          return lead as Lead
        })

      setLeads(parsedLeads)
      setCampaignStats({
        totalLeads: parsedLeads.length,
        emailsSent: 0,
        emailsFailed: 0,
      })
    } catch (error) {
      console.error("Error parsing CSV:", error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleSendEmails = async () => {
    if (!emailCredentials.email || !emailCredentials.appPassword) {
      alert("Please enter your email credentials first")
      return
    }

    if (leads.length === 0) {
      alert("Please upload a CSV file with leads first")
      return
    }

    setIsSendingEmails(true)

    try {
      const response = await fetch("/api/send-emails", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          leads,
          emailCredentials,
        }),
      })

      const result = await response.json()

      if (result.success) {
        setLeads(result.updatedLeads)
        setCampaignStats({
          totalLeads: result.updatedLeads.length,
          emailsSent: result.emailsSent,
          emailsFailed: result.emailsFailed,
        })
        alert(`Emails sent! ${result.emailsSent} successful, ${result.emailsFailed} failed`)
      } else {
        alert(`Error: ${result.error}`)
      }
    } catch (error) {
      console.error("Error sending emails:", error)
      alert("Error sending emails. Please try again.")
    } finally {
      setIsSendingEmails(false)
    }
  }

  const getScoreBadgeColor = (score: number) => {
    if (score >= 8) return "bg-green-500"
    if (score >= 5) return "bg-yellow-500"
    return "bg-red-500"
  }

  const getStatusBadge = (status?: string) => {
    if (status === "Sent") {
      return (
        <Badge className="bg-green-500 text-white">
          <CheckCircle className="h-3 w-3 mr-1" />
          Sent
        </Badge>
      )
    } else if (status?.startsWith("Failed")) {
      return (
        <Badge className="bg-red-500 text-white">
          <XCircle className="h-3 w-3 mr-1" />
          Failed
        </Badge>
      )
    } else {
      return <Badge variant="outline">Pending</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-foreground">AI Sales Campaign CRM</h1>
          <p className="text-muted-foreground">Manage leads and track email campaigns</p>
        </div>

        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Upload Lead Data
            </CardTitle>
            <CardDescription>Upload a CSV file containing your lead information</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="csv-upload">CSV File</Label>
                <Input id="csv-upload" type="file" accept=".csv" onChange={handleFileUpload} disabled={isUploading} />
              </div>
              {isUploading && <p className="text-sm text-muted-foreground">Processing file...</p>}
            </div>
          </CardContent>
        </Card>

        {/* Email Configuration Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="h-5 w-5" />
              Email Configuration
            </CardTitle>
            <CardDescription>Enter your Gmail credentials to send emails</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="email">Gmail Address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your-email@gmail.com"
                  value={emailCredentials.email}
                  onChange={(e) => setEmailCredentials({ ...emailCredentials, email: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="app-password">Gmail App Password</Label>
                <Input
                  id="app-password"
                  type="password"
                  placeholder="xxxx xxxx xxxx xxxx"
                  value={emailCredentials.appPassword}
                  onChange={(e) => setEmailCredentials({ ...emailCredentials, appPassword: e.target.value })}
                />
              </div>
            </div>
            <div className="mt-4">
              <Button
                onClick={handleSendEmails}
                disabled={isSendingEmails || leads.length === 0}
                className="w-full md:w-auto"
              >
                <Send className="h-4 w-4 mr-2" />
                {isSendingEmails ? "Sending Emails..." : "Send Emails to All Leads"}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Campaign Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Leads</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{campaignStats.totalLeads}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Emails Sent</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{campaignStats.emailsSent}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Failed Emails</CardTitle>
              <XCircle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{campaignStats.emailsFailed}</div>
            </CardContent>
          </Card>
        </div>

        {/* Leads Table */}
        {leads.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Lead Data
              </CardTitle>
              <CardDescription>Overview of all leads and their information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Lead ID</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Interest</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Persona</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {leads.map((lead) => (
                      <TableRow key={lead.LeadID}>
                        <TableCell className="font-mono text-sm">{lead.LeadID}</TableCell>
                        <TableCell>
                          {lead["First Name"]} {lead["Last Name"]}
                        </TableCell>
                        <TableCell className="text-sm">{lead.Email}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{lead["Interest Category"]}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={`text-white ${getScoreBadgeColor(Number(lead["Lead Score"]))}`}>
                            {lead["Lead Score"]}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">{lead["Buyer Persona"]}</Badge>
                        </TableCell>
                        <TableCell>{getStatusBadge(lead["Email Status"])}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Campaign Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Campaign Summary</CardTitle>
            <CardDescription>Key insights and recommendations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h4 className="font-semibold">Key Insights:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• All emails were successfully delivered</li>
                  <li>• High engagement expected from leads with score 8+</li>
                  <li>• Enterprise personas show highest lead scores</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">Recommendations:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Follow up with high-score leads first</li>
                  <li>• Segment campaigns by buyer persona</li>
                  <li>• Monitor email engagement metrics</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
