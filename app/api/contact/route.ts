import { NextRequest, NextResponse } from 'next/server'

interface ContactPayload {
  name: string
  email: string
  company?: string
  service?: string
  message: string
}

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export async function POST(req: NextRequest) {
  try {
    const body: ContactPayload = await req.json()

    if (!body.name?.trim() || !body.email?.trim() || !body.message?.trim()) {
      return NextResponse.json({ error: 'Name, email, and message are required.' }, { status: 400 })
    }

    if (!isValidEmail(body.email)) {
      return NextResponse.json({ error: 'Invalid email address.' }, { status: 400 })
    }

    if (body.message.trim().length < 10) {
      return NextResponse.json({ error: 'Message must be at least 10 characters.' }, { status: 400 })
    }

    // In production: send email via Resend/SendGrid/Postmark here
    console.log('New contact form submission:', {
      name: body.name,
      email: body.email,
      company: body.company,
      service: body.service,
      messageLength: body.message.length,
    })

    return NextResponse.json({ success: true, message: 'Thanks! We\'ll be in touch within 24 hours.' })
  } catch {
    return NextResponse.json({ error: 'Something went wrong. Please try again.' }, { status: 500 })
  }
}
