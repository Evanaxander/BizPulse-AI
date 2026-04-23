// BizPulse Invoice OCR Skill for OpenClaw
// Triggered when user sends an image with words like "invoice", "bill", "receipt"

const fs = require('fs');
const path = require('path');
const FormData = require('form-data');
const fetch = require('node-fetch');

const BIZPULSE_API = 'http://localhost:8000';

async function processInvoiceImage(imagePath, uploadedBy = 'whatsapp') {
    const form = new FormData();
    form.append('file', fs.createReadStream(imagePath));
    form.append('uploaded_by', uploadedBy);

    const response = await fetch(`${BIZPULSE_API}/invoices/process-image`, {
        method: 'POST',
        body: form,
        headers: form.getHeaders()
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
    }

    return await response.json();
}

async function getWeeklySummary() {
    const response = await fetch(`${BIZPULSE_API}/invoices/weekly-summary`);
    return await response.json();
}

// OpenClaw skill entry point
module.exports = {
    name: 'bizpulse-invoice',
    description: 'Process invoice images and track business expenses',
    triggers: ['invoice', 'bill', 'receipt', 'expense', 'summary', 'খরচ', 'বিল'],

    async run({ message, attachments, sendReply }) {
        // Weekly summary request
        if (message.toLowerCase().includes('summary') ||
            message.toLowerCase().includes('weekly') ||
            message.includes('সারসংক্ষেপ')) {
            const summary = await getWeeklySummary();
            return sendReply(
                `📊 *This Week's Expenses*\n\n` +
                `💰 Total: ${summary.total_expenses} ${summary.currency}\n` +
                `📄 Invoices: ${summary.invoice_count}\n` +
                `🏪 Vendors: ${summary.top_vendors.join(', ') || 'None yet'}\n\n` +
                `_Send a photo of any invoice to add it._`
            );
        }

        // Invoice image processing
        if (attachments && attachments.length > 0) {
            const image = attachments.find(a =>
                ['image/jpeg', 'image/png', 'image/webp'].includes(a.mimeType)
            );

            if (image) {
                await sendReply('🔍 Processing your invoice...');
                try {
                    const result = await processInvoiceImage(image.localPath);
                    return sendReply(
                        `✅ *Invoice Recorded*\n\n` +
                        `🏪 Vendor: ${result.vendor}\n` +
                        `💰 Amount: ${result.amount} ${result.currency}\n` +
                        `📅 Date: ${result.invoice_date || 'Not detected'}\n` +
                        `📦 Items: ${result.items ? JSON.parse(result.items).join(', ') : 'See full record'}\n\n` +
                        `_ID: #${result.id} saved successfully_`
                    );
                } catch (err) {
                    return sendReply(`❌ Could not read invoice: ${err.message}`);
                }
            }
        }

        return sendReply(
            '📋 *BizPulse Invoice Assistant*\n\n' +
            '• Send a photo of any invoice/bill to record it\n' +
            '• Type "summary" to see this week\'s expenses\n' +
            '• Supports Bangla and English invoices'
        );
    }
};