import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { LogOut, Plus, Search, Edit, Trash2, ChevronLeft, ChevronRight } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 10;

  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    course: '',
    status: 'active',
  });

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchStudents();
  }, [currentPage, searchTerm, statusFilter]);

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        limit,
      };

      if (searchTerm) params.search = searchTerm;
      if (statusFilter !== 'all') params.status = statusFilter;

      const { data } = await axios.get(`${BACKEND_URL}/api/students`, {
        params,
        withCredentials: true,
      });

      setStudents(data.students);
      setTotalPages(data.pages);
      setTotal(data.total);
    } catch (error) {
      toast.error('Failed to fetch students');
    } finally {
      setLoading(false);
    }
  };

  const handleAddStudent = async (e) => {
    e.preventDefault();

    if (!formData.name || !formData.email || !formData.course) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      await axios.post(`${BACKEND_URL}/api/students`, formData, {
        withCredentials: true,
      });
      toast.success('Student added successfully');
      setShowAddDialog(false);
      resetForm();
      fetchStudents();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to add student';
      toast.error(typeof errorMsg === 'string' ? errorMsg : 'Failed to add student');
    }
  };

  const handleEditStudent = async (e) => {
    e.preventDefault();

    if (!formData.name || !formData.email || !formData.course) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      await axios.put(`${BACKEND_URL}/api/students/${selectedStudent.id}`, formData, {
        withCredentials: true,
      });
      toast.success('Student updated successfully');
      setShowEditDialog(false);
      resetForm();
      fetchStudents();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to update student';
      toast.error(typeof errorMsg === 'string' ? errorMsg : 'Failed to update student');
    }
  };

  const handleDeleteStudent = async () => {
    try {
      await axios.delete(`${BACKEND_URL}/api/students/${selectedStudent.id}`, {
        withCredentials: true,
      });
      toast.success('Student deleted successfully');
      setShowDeleteDialog(false);
      setSelectedStudent(null);
      fetchStudents();
    } catch (error) {
      toast.error('Failed to delete student');
    }
  };

  const openEditDialog = (student) => {
    setSelectedStudent(student);
    setFormData({
      name: student.name,
      email: student.email,
      course: student.course,
      status: student.status,
    });
    setShowEditDialog(true);
  };

  const openDeleteDialog = (student) => {
    setSelectedStudent(student);
    setShowDeleteDialog(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      course: '',
      status: 'active',
    });
    setSelectedStudent(null);
  };

  const handleLogout = async () => {
    await logout();
    toast.success('Logged out successfully');
  };

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      <header className="bg-white border-b border-gray-200 px-8 py-4 flex justify-between items-center sticky top-0 z-50">
        <div>
          <h1 className="text-2xl tracking-tight font-semibold" style={{ fontFamily: 'Satoshi, sans-serif' }}>
            Student Management
          </h1>
          <p className="text-xs text-gray-500 mt-1" style={{ fontFamily: 'IBM Plex Sans, sans-serif' }}>
            Welcome, {user?.name || user?.email}
          </p>
        </div>
        <Button
          onClick={handleLogout}
          variant="outline"
          className="border border-gray-300 hover:bg-gray-50"
          data-testid="logout-button"
        >
          <LogOut className="w-4 h-4 mr-2" strokeWidth={1.5} />
          Logout
        </Button>
      </header>

      <div className="max-w-7xl mx-auto p-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-medium" style={{ fontFamily: 'Satoshi, sans-serif' }}>
              Students
            </h2>
            <p className="text-sm text-gray-500 mt-1">{total} total students</p>
          </div>
          <Button
            onClick={() => setShowAddDialog(true)}
            className="bg-black text-white hover:bg-gray-800 rounded-md px-4 py-2 text-sm font-medium transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-black"
            data-testid="add-student-button"
          >
            <Plus className="w-4 h-4 mr-2" strokeWidth={1.5} />
            Add Student
          </Button>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-gray-200 flex gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" strokeWidth={1.5} />
                <Input
                  placeholder="Search by name, email, or course..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="pl-10 border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
                  data-testid="search-input"
                />
              </div>
            </div>
            <div className="w-[180px]">
              <Select
                value={statusFilter}
                onValueChange={(value) => {
                  setStatusFilter(value);
                  setCurrentPage(1);
                }}
              >
                <SelectTrigger className="border-gray-300" data-testid="status-filter">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="overflow-x-auto">
            {loading ? (
              <div className="p-8 text-center text-gray-500">Loading...</div>
            ) : students.length === 0 ? (
              <div className="p-8 text-center text-gray-500">No students found</div>
            ) : (
              <table className="w-full text-sm text-left border-collapse" data-testid="students-table">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-200">
                    <th className="text-gray-500 font-medium py-3 px-4">Name</th>
                    <th className="text-gray-500 font-medium py-3 px-4">Email</th>
                    <th className="text-gray-500 font-medium py-3 px-4">Course</th>
                    <th className="text-gray-500 font-medium py-3 px-4">Status</th>
                    <th className="text-gray-500 font-medium py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student) => (
                    <tr
                      key={student.id}
                      className="border-b border-gray-100 hover:bg-gray-50"
                      data-testid={`student-row-${student.id}`}
                    >
                      <td className="py-4 px-4">{student.name}</td>
                      <td className="py-4 px-4 text-gray-600">{student.email}</td>
                      <td className="py-4 px-4">{student.course}</td>
                      <td className="py-4 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                            student.status === 'active'
                              ? 'bg-green-50 text-green-700 border border-green-200'
                              : 'bg-gray-50 text-gray-700 border border-gray-200'
                          }`}
                        >
                          {student.status}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex gap-2">
                          <Button
                            onClick={() => openEditDialog(student)}
                            variant="outline"
                            size="sm"
                            className="border-gray-300 hover:bg-gray-50"
                            data-testid={`edit-button-${student.id}`}
                          >
                            <Edit className="w-3 h-3" strokeWidth={1.5} />
                          </Button>
                          <Button
                            onClick={() => openDeleteDialog(student)}
                            variant="outline"
                            size="sm"
                            className="border-red-300 text-red-600 hover:bg-red-50"
                            data-testid={`delete-button-${student.id}`}
                          >
                            <Trash2 className="w-3 h-3" strokeWidth={1.5} />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {totalPages > 1 && (
            <div className="p-4 border-t border-gray-200 flex justify-between items-center">
              <div className="text-sm text-gray-500">
                Page {currentPage} of {totalPages}
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  variant="outline"
                  size="sm"
                  className="border-gray-300"
                  data-testid="prev-page-button"
                >
                  <ChevronLeft className="w-4 h-4" strokeWidth={1.5} />
                </Button>
                <Button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  variant="outline"
                  size="sm"
                  className="border-gray-300"
                  data-testid="next-page-button"
                >
                  <ChevronRight className="w-4 h-4" strokeWidth={1.5} />
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add Student Dialog */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent className="bg-white rounded-lg shadow-xl border border-gray-200" data-testid="add-student-dialog">
          <DialogHeader>
            <DialogTitle className="text-xl font-medium" style={{ fontFamily: 'Satoshi, sans-serif' }}>
              Add New Student
            </DialogTitle>
            <DialogDescription className="text-sm text-gray-500">
              Fill in the details to add a new student to the system.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAddStudent} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="add-name">Name</Label>
              <Input
                id="add-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
                data-testid="add-name-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-email">Email</Label>
              <Input
                id="add-email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
                data-testid="add-email-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-course">Course</Label>
              <Input
                id="add-course"
                value={formData.course}
                onChange={(e) => setFormData({ ...formData, course: e.target.value })}
                className="border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
                data-testid="add-course-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-status">Status</Label>
              <Select
                value={formData.status}
                onValueChange={(value) => setFormData({ ...formData, status: value })}
              >
                <SelectTrigger className="border-gray-300" data-testid="add-status-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowAddDialog(false);
                  resetForm();
                }}
                className="border-gray-300"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                className="bg-black text-white hover:bg-gray-800"
                data-testid="add-submit-button"
              >
                Add Student
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Student Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="bg-white rounded-lg shadow-xl border border-gray-200" data-testid="edit-student-dialog">
          <DialogHeader>
            <DialogTitle className="text-xl font-medium" style={{ fontFamily: 'Satoshi, sans-serif' }}>
              Edit Student
            </DialogTitle>
            <DialogDescription className="text-sm text-gray-500">
              Update the student information below.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleEditStudent} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Name</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
                data-testid="edit-name-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-email">Email</Label>
              <Input
                id="edit-email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
                data-testid="edit-email-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-course">Course</Label>
              <Input
                id="edit-course"
                value={formData.course}
                onChange={(e) => setFormData({ ...formData, course: e.target.value })}
                className="border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
                data-testid="edit-course-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-status">Status</Label>
              <Select
                value={formData.status}
                onValueChange={(value) => setFormData({ ...formData, status: value })}
              >
                <SelectTrigger className="border-gray-300" data-testid="edit-status-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowEditDialog(false);
                  resetForm();
                }}
                className="border-gray-300"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                className="bg-black text-white hover:bg-gray-800"
                data-testid="edit-submit-button"
              >
                Save Changes
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent className="bg-white rounded-lg shadow-xl border border-gray-200" data-testid="delete-confirmation-dialog">
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete {selectedStudent?.name}'s record. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-gray-300">Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteStudent}
              className="bg-red-600 text-white hover:bg-red-700"
              data-testid="confirm-delete-button"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Dashboard;
