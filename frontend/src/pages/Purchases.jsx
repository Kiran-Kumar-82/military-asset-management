import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'
import api from '../services/api'
import { format } from 'date-fns'

export default function Purchases() {
  const [purchases, setPurchases] = useState([])
  const [bases, setBases] = useState([])
  const [assetTypes, setAssetTypes] = useState([])
  const [loading, setLoading] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingPurchase, setEditingPurchase] = useState(null)
  const [formData, setFormData] = useState({
    base: '',
    asset_type: '',
    quantity: '',
    purchase_date: new Date(),
    purchase_cost: '',
    supplier: '',
    notes: '',
  })

  useEffect(() => {
    fetchPurchases()
    fetchBases()
    fetchAssetTypes()
  }, [])

  const fetchPurchases = async () => {
    setLoading(true)
    try {
      const response = await api.get('/assets/purchases/')
      setPurchases(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch purchases:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchBases = async () => {
    try {
      const response = await api.get('/assets/bases/')
      setBases(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch bases:', error)
    }
  }

  const fetchAssetTypes = async () => {
    try {
      const response = await api.get('/assets/asset-types/')
      setAssetTypes(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch asset types:', error)
    }
  }

  const handleOpenDialog = (purchase = null) => {
    if (purchase) {
      setEditingPurchase(purchase)
      setFormData({
        base: purchase.base,
        asset_type: purchase.asset_type,
        quantity: purchase.quantity,
        purchase_date: new Date(purchase.purchase_date),
        purchase_cost: purchase.purchase_cost || '',
        supplier: purchase.supplier || '',
        notes: purchase.notes || '',
      })
    } else {
      setEditingPurchase(null)
      setFormData({
        base: '',
        asset_type: '',
        quantity: '',
        purchase_date: new Date(),
        purchase_cost: '',
        supplier: '',
        notes: '',
      })
    }
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingPurchase(null)
  }

  const handleSubmit = async () => {
    try {
      const data = {
        ...formData,
        purchase_date: format(formData.purchase_date, 'yyyy-MM-dd'),
      }
      if (editingPurchase) {
        await api.put(`/assets/purchases/${editingPurchase.id}/`, data)
      } else {
        await api.post('/assets/purchases/', data)
      }
      handleCloseDialog()
      fetchPurchases()
    } catch (error) {
      console.error('Failed to save purchase:', error)
      alert('Failed to save purchase: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this purchase?')) {
      try {
        await api.delete(`/assets/purchases/${id}/`)
        fetchPurchases()
      } catch (error) {
        console.error('Failed to delete purchase:', error)
        alert('Failed to delete purchase')
      }
    }
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4">Purchases</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            New Purchase
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Base</TableCell>
                <TableCell>Asset Type</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Purchase Date</TableCell>
                <TableCell>Cost</TableCell>
                <TableCell>Supplier</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {purchases.map((purchase) => (
                <TableRow key={purchase.id}>
                  <TableCell>{purchase.base_name}</TableCell>
                  <TableCell>{purchase.asset_type_name}</TableCell>
                  <TableCell>{purchase.quantity}</TableCell>
                  <TableCell>{purchase.purchase_date}</TableCell>
                  <TableCell>{purchase.purchase_cost || 'N/A'}</TableCell>
                  <TableCell>{purchase.supplier || 'N/A'}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(purchase)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(purchase.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingPurchase ? 'Edit Purchase' : 'New Purchase'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <TextField
                select
                label="Base"
                value={formData.base}
                onChange={(e) => setFormData({ ...formData, base: e.target.value })}
                fullWidth
              >
                {bases.map((base) => (
                  <MenuItem key={base.id} value={base.id}>
                    {base.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Asset Type"
                value={formData.asset_type}
                onChange={(e) =>
                  setFormData({ ...formData, asset_type: e.target.value })
                }
                fullWidth
              >
                {assetTypes.map((type) => (
                  <MenuItem key={type.id} value={type.id}>
                    {type.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                label="Quantity"
                type="number"
                value={formData.quantity}
                onChange={(e) =>
                  setFormData({ ...formData, quantity: e.target.value })
                }
                fullWidth
                required
              />
              <DatePicker
                label="Purchase Date"
                value={formData.purchase_date}
                onChange={(date) =>
                  setFormData({ ...formData, purchase_date: date })
                }
                slotProps={{
                  textField: {
                    fullWidth: true,
                  },
                }}
              />
              <TextField
                label="Purchase Cost"
                type="number"
                value={formData.purchase_cost}
                onChange={(e) =>
                  setFormData({ ...formData, purchase_cost: e.target.value })
                }
                fullWidth
              />
              <TextField
                label="Supplier"
                value={formData.supplier}
                onChange={(e) =>
                  setFormData({ ...formData, supplier: e.target.value })
                }
                fullWidth
              />
              <TextField
                label="Notes"
                multiline
                rows={3}
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                fullWidth
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button onClick={handleSubmit} variant="contained">
              {editingPurchase ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  )
}

