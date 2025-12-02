import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { invoiceAPI, syncAPI, VendorInvoice } from '@/api/client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle, XCircle, Loader2, ArrowLeft, AlertCircle } from 'lucide-react'
import { format } from 'date-fns'

export default function Review() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [invoice, setInvoice] = useState<VendorInvoice | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [poNumber, setPoNumber] = useState('')
  const [poData, setPoData] = useState<any>(null)
  const [loadingPO, setLoadingPO] = useState(false)
  const [poError, setPoError] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    if (id) {
      loadInvoice(parseInt(id))
    }
  }, [id])

  useEffect(() => {
    if (poNumber.trim()) {
      loadPurchaseOrder(poNumber.trim())
    } else {
      setPoData(null)
      setPoError('')
    }
  }, [poNumber])

  const loadInvoice = async (invoiceId: number) => {
    try {
      setLoading(true)
      const data = await invoiceAPI.get(invoiceId)
      setInvoice(data)
      if (data.po_numbers && data.po_numbers.length > 0) {
        setPoNumber(data.po_numbers[0])
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load invoice')
    } finally {
      setLoading(false)
    }
  }

  const loadPurchaseOrder = async (po: string) => {
    try {
      setLoadingPO(true)
      setPoError('')
      const data = await syncAPI.getPurchaseOrder(po)
      setPoData(data)
    } catch (err: any) {
      setPoError(err.response?.data?.detail || 'Failed to load purchase order')
      setPoData(null)
    } finally {
      setLoadingPO(false)
    }
  }

  const handleSync = async () => {
    if (!invoice || !poNumber.trim()) {
      setError('Please enter a PO number')
      return
    }

    setSyncing(true)
    setError('')
    setSuccess('')

    try {
      const result = await syncAPI.sync(invoice.id, poNumber.trim())
      if (result.success) {
        setSuccess(result.message || 'Invoice synced successfully!')
        // Reload invoice to get updated status
        await loadInvoice(invoice.id)
      } else {
        setError(result.message || result.error || 'Sync failed')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Sync failed. Please try again.')
    } finally {
      setSyncing(false)
    }
  }

  const handleUpdate = async (field: string, value: any) => {
    if (!invoice) return

    try {
      const updated = await invoiceAPI.update(invoice.id, { [field]: value })
      setInvoice(updated)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Update failed')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!invoice) {
    return (
      <div className="bg-destructive/10 text-destructive p-4 rounded-md">
        Invoice not found
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" onClick={() => navigate('/')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Review Invoice</h1>
          <p className="text-gray-600 mt-1">Review and sync invoice to Plex ERP</p>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-md flex items-center space-x-2">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-800 p-4 rounded-md flex items-center space-x-2">
          <CheckCircle className="h-5 w-5" />
          <span>{success}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Invoice Details */}
        <Card>
          <CardHeader>
            <CardTitle>Invoice Details</CardTitle>
            <CardDescription>Extracted information from the invoice</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Invoice Number</Label>
              <Input
                value={invoice.invoice_number}
                onChange={(e) => handleUpdate('invoice_number', e.target.value)}
                onBlur={(e) => handleUpdate('invoice_number', e.target.value)}
              />
            </div>
            <div>
              <Label>Vendor Name</Label>
              <Input
                value={invoice.vendor_name}
                onChange={(e) => handleUpdate('vendor_name', e.target.value)}
                onBlur={(e) => handleUpdate('vendor_name', e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Invoice Date</Label>
                <Input
                  type="date"
                  value={invoice.invoice_date ? (typeof invoice.invoice_date === 'string' ? invoice.invoice_date.split('T')[0] : invoice.invoice_date) : ''}
                  onChange={(e) => handleUpdate('invoice_date', e.target.value)}
                />
              </div>
              <div>
                <Label>Due Date</Label>
                <Input
                  type="date"
                  value={invoice.due_date ? (typeof invoice.due_date === 'string' ? invoice.due_date.split('T')[0] : invoice.due_date) : ''}
                  onChange={(e) => handleUpdate('due_date', e.target.value)}
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label>Subtotal</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={invoice.subtotal || ''}
                  onChange={(e) => handleUpdate('subtotal', parseFloat(e.target.value) || null)}
                />
              </div>
              <div>
                <Label>Tax</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={invoice.tax_amount || ''}
                  onChange={(e) => handleUpdate('tax_amount', parseFloat(e.target.value) || null)}
                />
              </div>
              <div>
                <Label>Total</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={invoice.total_amount || ''}
                  onChange={(e) => handleUpdate('total_amount', parseFloat(e.target.value) || null)}
                />
              </div>
            </div>
            {(invoice.confidence_score ?? invoice.confidence) != null && (
              <div>
                <Label>AI Confidence</Label>
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        (invoice.confidence_score ?? invoice.confidence ?? 0) >= 80
                          ? 'bg-green-500'
                          : (invoice.confidence_score ?? invoice.confidence ?? 0) >= 60
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${invoice.confidence_score ?? invoice.confidence ?? 0}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600">
                    {((invoice.confidence_score ?? invoice.confidence ?? 0) as number).toFixed(1)}%
                  </span>
                </div>
              </div>
            )}
            <div>
              <Label>Status</Label>
              <div className="mt-1">
                <span
                  className={`px-3 py-1 text-sm rounded-full ${
                    invoice.status === 'synced'
                      ? 'bg-green-100 text-green-800'
                      : invoice.status === 'pending'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {invoice.status}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

      </div>

      {/* Purchase Order Details - Full Width Card Between Invoice and Sync */}
      {poNumber.trim() && (
        <Card>
          <CardHeader>
            <CardTitle>Purchase Order Details</CardTitle>
            <CardDescription>Purchase order information from Plex ERP</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {loadingPO ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
                <span className="ml-2 text-gray-600">Loading purchase order...</span>
              </div>
            ) : poError ? (
              <div className="bg-destructive/10 text-destructive p-4 rounded-md flex items-center space-x-2">
                <AlertCircle className="h-5 w-5" />
                <span>{poError}</span>
              </div>
            ) : poData ? (
              <>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <Label className="text-xs text-gray-500">PO Number</Label>
                    <p className="font-medium">{poData.poNumber || poData.po_number || poNumber}</p>
                  </div>
                  <div>
                    <Label className="text-xs text-gray-500">Status</Label>
                    <p className="font-medium">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        (poData.status || '').toLowerCase() === 'open' ? 'bg-green-100 text-green-800' :
                        (poData.status || '').toLowerCase() === 'closed' ? 'bg-gray-100 text-gray-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {poData.status || 'Unknown'}
                      </span>
                    </p>
                  </div>
                  <div>
                    <Label className="text-xs text-gray-500">Total Amount</Label>
                    <p className="font-medium">
                      {poData.totalAmount || poData.total_amount 
                        ? `$${(poData.totalAmount || poData.total_amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                        : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <Label className="text-xs text-gray-500">Currency</Label>
                    <p className="font-medium">{poData.currencyCode || poData.currency || 'USD'}</p>
                  </div>
                </div>

                {poData.vendorName || poData.vendor_name ? (
                  <div>
                    <Label className="text-xs text-gray-500">Vendor</Label>
                    <p className="font-medium">{poData.vendorName || poData.vendor_name}</p>
                  </div>
                ) : null}

                {poData.lineItems || poData.line_items ? (
                  <div>
                    <Label className="text-xs text-gray-500 mb-2 block">Line Items</Label>
                    <div className="border rounded-md overflow-hidden">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Line</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Part Number</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Description</th>
                            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Quantity</th>
                            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Unit Price</th>
                            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Total</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {(poData.lineItems || poData.line_items || []).map((item: any, index: number) => (
                            <tr key={index}>
                              <td className="px-4 py-2">{item.lineNumber || item.line_number || index + 1}</td>
                              <td className="px-4 py-2">{item.partNumber || item.part_number || 'N/A'}</td>
                              <td className="px-4 py-2">{item.description || 'N/A'}</td>
                              <td className="px-4 py-2 text-right">{item.quantity || 0}</td>
                              <td className="px-4 py-2 text-right">
                                {item.unitPrice || item.unit_price 
                                  ? `$${(item.unitPrice || item.unit_price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                                  : 'N/A'}
                              </td>
                              <td className="px-4 py-2 text-right">
                                {item.lineTotal || item.line_total 
                                  ? `$${(item.lineTotal || item.line_total).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                                  : 'N/A'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : null}
              </>
            ) : (
              <p className="text-gray-500 text-sm">Enter a PO number above to view purchase order details</p>
            )}
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sync to Plex - Moved to bottom */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Sync to Plex ERP</CardTitle>
            <CardDescription>Match this invoice to a purchase order and sync</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>PO Number</Label>
              <Input
                value={poNumber}
                onChange={(e) => setPoNumber(e.target.value)}
                placeholder="Enter PO number"
              />
              {invoice.po_numbers && invoice.po_numbers.length > 0 && (
                <p className="text-xs text-gray-500 mt-1">
                  Detected PO numbers: {invoice.po_numbers.join(', ')}
                </p>
              )}
            </div>

            <Button onClick={handleSync} disabled={syncing || !poNumber.trim() || !poData} className="w-full">
              {syncing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Syncing...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Sync to Plex
                </>
              )}
            </Button>

            {invoice.status === 'synced' && (
              <div className="bg-green-50 border border-green-200 p-4 rounded-md">
                <div className="flex items-center space-x-2 text-green-800">
                  <CheckCircle className="h-5 w-5" />
                  <span className="font-medium">Successfully synced to Plex ERP</span>
                </div>
              </div>
            )}

            <div className="pt-4 border-t">
              <h4 className="font-medium mb-2">Invoice Metadata</h4>
              <div className="text-sm text-gray-600 space-y-1">
                {invoice.created_at && (
                  <p>
                    <span className="font-medium">Created:</span>{' '}
                    {format(new Date(invoice.created_at), 'MMM dd, yyyy HH:mm')}
                  </p>
                )}
                {invoice.updated_at && (
                  <p>
                    <span className="font-medium">Updated:</span>{' '}
                    {format(new Date(invoice.updated_at), 'MMM dd, yyyy HH:mm')}
                  </p>
                )}
                {invoice.file_path && (
                  <p>
                    <span className="font-medium">File:</span> {invoice.file_path.split('/').pop()}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

