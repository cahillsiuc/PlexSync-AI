import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { invoiceAPI, VendorInvoice } from '@/api/client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload as UploadIcon, FileText, CheckCircle, AlertCircle } from 'lucide-react'

export default function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadedInvoice, setUploadedInvoice] = useState<VendorInvoice | null>(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError('')
      setUploadedInvoice(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError('')

    try {
      const invoice = await invoiceAPI.upload(file)
      setUploadedInvoice(invoice)
      setFile(null)
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement
      if (fileInput) fileInput.value = ''
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleReview = () => {
    if (uploadedInvoice) {
      navigate(`/review/${uploadedInvoice.id}`)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Invoice</h1>
        <p className="text-gray-600 mt-1">Upload a PDF or image of your invoice to get started</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload Invoice File</CardTitle>
          <CardDescription>
            Supported formats: PDF, PNG, JPG, JPEG. The AI will automatically extract invoice details.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="bg-destructive/10 text-destructive p-4 rounded-md flex items-center space-x-2">
              <AlertCircle className="h-5 w-5" />
              <span>{error}</span>
            </div>
          )}

          {uploadedInvoice ? (
            <div className="bg-green-50 border border-green-200 p-6 rounded-lg space-y-4">
              <div className="flex items-center space-x-2 text-green-800">
                <CheckCircle className="h-5 w-5" />
                <h3 className="font-semibold">Invoice uploaded successfully!</h3>
              </div>
              <div className="space-y-2 text-sm">
                <p>
                  <span className="font-medium">Invoice Number:</span> {uploadedInvoice.invoice_number}
                </p>
                <p>
                  <span className="font-medium">Vendor:</span> {uploadedInvoice.vendor_name}
                </p>
                {uploadedInvoice.total_amount && (
                  <p>
                    <span className="font-medium">Total Amount:</span> $
                    {uploadedInvoice.total_amount.toLocaleString('en-US', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </p>
                )}
                {(uploadedInvoice.confidence_score ?? uploadedInvoice.confidence) && (
                  <p>
                    <span className="font-medium">Confidence:</span> {(uploadedInvoice.confidence_score ?? uploadedInvoice.confidence ?? 0).toFixed(1)}%
                  </p>
                )}
              </div>
              <div className="flex space-x-2">
                <Button onClick={handleReview}>Review & Sync</Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setUploadedInvoice(null)
                    setFile(null)
                  }}
                >
                  Upload Another
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary transition-colors">
                <input
                  id="file-input"
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="file-input" className="cursor-pointer">
                  <div className="flex flex-col items-center space-y-4">
                    <div className="bg-gray-100 p-4 rounded-full">
                      <UploadIcon className="h-8 w-8 text-gray-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">
                        {file ? file.name : 'Click to upload or drag and drop'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">PDF, PNG, JPG up to 10MB</p>
                    </div>
                    {file && (
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <FileText className="h-4 w-4" />
                        <span>{file.name}</span>
                        <span className="text-gray-400">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                      </div>
                    )}
                  </div>
                </label>
              </div>

              <Button onClick={handleUpload} disabled={!file || uploading} className="w-full">
                {uploading ? 'Uploading and parsing...' : 'Upload Invoice'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

